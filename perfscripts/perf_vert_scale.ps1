##---------------------------------------------------##
# Scripts for Performance and Vertical scale
##---------------------------------------------------##
Add-PSSnapin vmware.vimautomation.core
Import-Module VMware.VimAutomation.Vds

$linuxHost = '172.16.10.2'
$password = 'VMware1!'
$sUser = 'vmware'

$secpasswd = ConvertTo-SecureString "VMware1!" -AsPlainText -Force
$mycreds = New-Object System.Management.Automation.PSCredential ($sUser, $secpasswd)

$clusterName = 'PerfCluster'

Function connectToVC([string] $vc, [string] $username, [string] $password) {
connect-viserver -server $vc -User $username -Password $password
 
}

Function disconnectFromVC([string] $vc) {
    Disconnect-VIServer -Server $vc -Confirm:$false
}

## Before calling this ensure that connection to vCenter
## If needed please disconnect from the vCenter.
## if used in a loop (ie ading lots of hosts) do not need to connect/disconnect 
## for each host
## licenseKey=4N20N-QYN9Q-L8F8T-0RAU4-0TN05
###
Function addHostToVC ([string] $esxHost, [string] $clusterToAdd, [string] $username, [string] $password, [string] $licenseKey) {
   
    $esxInfo = Add-VMHost -Name $esxHost -Location $clusterToAdd -User $username -Password $password  -force -ErrorAction SilentlyContinue
    if($esxInfo -eq $null) {
        Write-Host -ForegroundColor DarkYellow "$esxHost not added , either it is already there or non reachable"
        return
    }
    Set-VMHost -VMHost $esxHost -LicenseKey $licenseKey -State Connected
    Write-Host -ForegroundColor GREEN " Added $esxHost to vCenter"
}

Function createVDS( [string] $dataCenter, [string] $vdsname, [int] $switchMTU, [int] $numUplinks) {

    if($numUplinks -eq 0) {
        New-VDSwitch -Name $vdsname -Location $dataCenter -mtu $switchMTU
    } elseif ($numUplinks -gt 0) {
        New-VDSwitch -Name $vdsname -Location $dataCenter -mtu $switchMTU -NumUplinkPorts $numUplinks
    } else {
        Write-Host -ForegroundColor RED " negative number of uplinks $numUplinks specified "
    }

}

# Specify numports, will need for vertical scale where you will have
# lots of VM
Function createVDSPG([string] $dataCenter, [string] $vdsname, [string] $portGroup, [int] $numPorts) {

    $dvswithIno = Get-VDSwitch -Name $vdsname -Location $dataCenter
    if($numPorts -eq 0) {
        New-VDPortgroup -Name $portGroup -VDSwitch $dvswithIno -NumPorts $numPorts
    } else {
        New-VDPortgroup -Name $portGroup -VDSwitch $dvswithIno -NumPorts $numPorts
    }
    Write-Host -ForegroundColor GREEN "Added PG $portGroup in to VDS $vdsname"

}

Function addHostToVDS([string] $esxHost, [string] $vdsName) {


    $VDSwitch = Get-VDSwitch -Name $vdsName
    $VDSwitch |  Add-VDSwitchVMHost -VMHost $esxHost -Confirm:$false

    Write-Host -ForegroundColor GREEN " Added $esxHost to vDS: $vdsName"


}

Function addVmnicToVDS([string] $esxHost, [string] $vdsName, [string] $vmnic) {

    $VDSwitch = Get-VDSwitch -Name $vdsName
    

    #Get physical adapter to move
    $VMHostObj = Get-VMHost $esxHost
    $vmhostadapter = $VMHostObj | Get-VMHostNetworkAdapter -Physical -Name $vmnic 
    
    $VDSwitch | Add-VDSwitchPhysicalNetworkAdapter -VMHostNetworkAdapter $vmhostadapter -Confirm:$false

    Write-Host -ForegroundColor GREEN " Added $vmnic on $esxHost to vDS: $vdsName"

}

Function moveVMPG([string] $vmName, [string] $oldPG, [string] $newPG) {

    Get-VM -Name $vmName |Get-NetworkAdapter |Where {$_.NetworkName -eq $OldPG } |Set-NetworkAdapter -NetworkName $newPG -Confirm:$false -StartConnected:$true -RunAsync
    Write-Host -ForegroundColor GREEN " Moved $vmName to $newPG "

}
Function scanStorage([string] $esxHost) {
    
    $esxInfo = Get-VMHost -Name $esxHost -ErrorAction SilentlyContinue
    
     if ($esxInfo -eq $null) {
       Write-Host -ForegroundColor GRAY " $esxHost ESX HOST is not present in the inventory"
       return
    }

    Get-VMHostStorage -VMHost $esxInfo -RescanAllHBA -RescanVmfs -Refresh
    Write-Host -ForegroundColor Green "Storage Scan for $esxHost complete"
}

Function powerOnVM([string] $vmName) {
    $vmInfo = Get-VM -Name $vmName
    Start-VM -VM $vmInfo -Confirm:$false -RunAsync
    Write-Host -ForegroundColor GREEN " PoweredOn $vmName"
}

Function powerOffVM([string] $vmName) {

    $vmInfo = Get-VM -Name $vmName
    Stop-VM -VM $vmInfo -Confirm:$false -RunAsync
    Write-Host -ForegroundColor GREEN " PoweredOff $vmName"

}

#Performs Guest OS Shutdown
Function shutDownVM([string] $vmName) {

    $vmInfo = Get-VM -Name $vmName
    if($vmInfo.PowerState -ne 'PoweredOff') {
        Shutdown-VMGuest -VM $vmInfo -Confirm:$false
    }
    Write-Host -ForegroundColor GREEN " ShutDown $vmName"

}


Function powerOnIxia() {

    #Power on the virtual cards first
    powerOnVM 'Ixia_card_1'
    powerOnVM 'Ixia_card_2'
    powerOnVM 'Ixia_card_3'
    powerOnVM 'Ixia_card_4'
    powerOnVM 'Ixia_card_5'
    powerOnVM 'Ixia_card_6'

    #wait for 120 seconds
    Write-Host -ForegroundColor Magenta "There is a wait of 60 Sec before powerON Chassis - Patience "
    [Console]::Out.Flush() 
    Start-Sleep -Seconds 120

    #start the chassis
    powerOnVM 'Ixia_Chassis'
    Write-Host -ForegroundColor GREEN "IXIA Powered ON"
}

Function shutDownIxia() {

    shutDownVM 'Ixia_Chassis'

    
    shutDownVM 'Ixia_card_1'
    shutDownVM 'Ixia_card_2'
    shutDownVM 'Ixia_card_3'
    shutDownVM 'Ixia_card_4'
    shutDownVM 'Ixia_card_5'
    shutDownVM 'Ixia_card_6'
    
    Write-Host -ForegroundColor GREEN "IXIA is now Powered Off"
}
##
# passing $false below only remove from the inventory
# if need to delete from the inventory and disk pass $true
##

Function deleteIxia() {

    deleteVM 'Ixia_Chassis' $false

    
    deleteVM 'Ixia_card_1' $false
    deleteVM 'Ixia_card_2' $false
    deleteVM 'Ixia_card_3' $false
    deleteVM 'Ixia_card_4' $false
    deleteVM 'Ixia_card_5' $false
    deleteVM 'Ixia_card_6' $false
    
    Write-Host -ForegroundColor GREEN "IXIA modules deleted"

}
##
# This is higly tailored function for our specific use
# $VMXDataStore must be specified with two angle brackets e.g "[VM-DataStore]"
# also the specified data store must be mounted on the esx host
##

Function registerLinuxVMs([string] $esxHost, [string] $VMXDataStore, [int] $StartNumOfVM, [int] $endNumOfVM) {
#$VMXDataStore = "[VM-DataStore]"


    For ( $num=$StartNumOfVM;$num -le $endNumOfVM;$num++) { 
    
   
        $VMXFile = "$VMXDataStore Linux-VM$num/Linux-VM$num.vmx"
  
        $newVM = New-VM -VMFilePath $VMXFile -VMHost $ESXHost -RunAsync -ErrorAction SilentlyContinue
        if($newVM -eq $null) {
            Write-Host -ForegroundColor DarkRed "VM Linux-VM$num was not added due to error"
        } else {
            Write-Host -ForegroundColor GREEN "added VM $VMXFile to host $ESXHost"
        }
    } 


}

Function deleteVM([string] $vmName, [string] $deletePermenantly) {
    
  
   $vmInfo = Get-VM -Name $vmName -ErrorAction SilentlyContinue
    
    if ($vmInfo -eq $null) {
       Write-Host -ForegroundColor GRAY " $vmName VM is not present in the inventory"
       return
    }
    if($vmInfo.PowerState -eq 'PoweredOn') {
        shutDownVM $vmName
        while ($vmInfo.PowerState -eq 'PoweredOn') {
            Start-Sleep -Seconds 10
            $vmInfo = Get-VM -Name $vmName
        }
        $vmInfo = Get-VM -Name $vmName
    }
    if($deletePermenantly -eq $true) {
        Remove-VM -VM $vmInfo -Confirm:$false -RunAsync -DeletePermanently
    } else {
        Remove-VM -VM $vmInfo -Confirm:$false -RunAsync
    }
    Write-Host -ForegroundColor GREEN " Removed $vmName from the inventory"

}

function Show-Menu
{
     param (
           [string]$Title = 'Menu'
     )
     
     Write-Host "================ $Title ================"
     
     Write-Host "1: Enter '1' To Perform Infrastructure Setup"
     Write-Host "2: Enter '2' To Power up IXIA also move to the Port Group"
     Write-Host "3: Enter '3' To PowerOff IXIA and move out from Port Group"
     Write-Host "4: Enter '4' To Remove IXIA VM from the VC inventory"
     Write-Host "5: Enter '5' To Add vertical Scale VM and enable infra for vertical testing"
     Write-Host "6: Enter '6' To Add interfaces to Linux VM"
     Write-Host "7: Enter '7' To Power on Linux VM"
     Write-Host "8: Enter '8' To Configure IP Address on Linux"
     Write-Host "9: Enter '9' To Power Off Linux VMS"
     Write-Host "10: Enter '10' To Remove Linux VMS from the VC inventory"
     Write-Host "11: Enter '11' To Clear Infrastructure Setup"
     Write-Host "Q: Enter 'Q' to quit."
}

Function Select-Choice() {
    do
    {
         Show-Menu
         $input = Read-Host "Please make a selection"
         switch ($input)
         {
               '1' {
                  prepareInfra $clusterName
               } '2' {
                  readyPerfInfra
               } '3' {
                    
                  powerOffPerfInfra
               }
               '4' {
                  deleteIxia
               }

               '5' {
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  prepareVerticalScale $start $end
               }
               '6' {
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  [int]$numOfInf = Read-Host -Prompt "Enter number of interfaces to be added"
                  AddInterfacesToLinuxVM $start $end $numOfInf 'VDS_vertical_scale_pg'
               }
               
               '7' {#
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  powerOnLinuxVM $start $end
               } 
               '8' {
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  connectAndAddIP $start $end
               } 
               
               '9'{
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  shutDownLinuxVMs $start $end
               } 

               '10'{
                  [int]$start = Read-Host -Prompt "Enter Starting Linx VM"
                  [int]$end  = Read-Host -Prompt "Enter Ending Linux VM"
                  deleteLinuxVMs $start $end
               } 
               '11' {
                  clearInfraConfig $clusterName
                  
               }

               'q' {
                    return
               }
         }
         pause
    } until ($input -eq 'q')
}


Function checkDataStores([string] $esxHost, [string] $datastore, [Ref]$results) {
     $esxInfo = Get-VMHost -Name $esxHost -ErrorAction SilentlyContinue
    
     if ($esxInfo -eq $null) {
       Write-Host -ForegroundColor GRAY " $esxHost ESX HOST is not present in the inventory"
       return
    }

    $dstore = Get-Datastore -VMHost $esxInfo -ErrorAction SilentlyContinue
    $results.value = $false
    foreach ($ds in $dstore) {
        Write-Host "Found datastore $ds"
        if($ds.Name -eq $datastore) {
            $results.value = $true
            return
        }
    }
   
}


Function addClusterToVC ([string] $LocationName,  [string] $clusterName) {
   
    #for debug
    #Write-Host "addClusterToVC: Location [$LocationName] Cluster [$clusterName]"

    $clusterInfo = New-Cluster -Location $LocationName -Name $clusterName -DRSEnabled -DrsAutomationLevel  Manual -ErrorAction Stop

    if($clusterInfo -eq $null) {
        Write-Host -ForegroundColor DarkYellow "ERROR: Cluster [$clusterName] not added"
        return
    }
    
    Write-Host -ForegroundColor GREEN " Added Cluster[$clusterName] to vCenter"
}


Function deleteClusterFromVC ([string] $clusterName) {
   
    #for debug
    #Write-Host "deleteClusterFromVC: Cluster [$clusterName]"

    $clusterInfo = Remove-Cluster $clusterName -Confirm:$false -ErrorAction SilentlyContinue

    Write-Host -ForegroundColor GREEN " Deleted Cluster[$clusterName] from vCenter"
}


Function prepareInfra([string] $perfClusterName) {


        $dataCenter = 'Cert-DC'
    # add cluster
        addClusterToVC $dataCenter $perfClusterName

    # add esx-perf to vCenter
        addHostToVC 'esx-perf.corp.local' $perfClusterName 'root' 'VMware1!' '4N20N-QYN9Q-L8F8T-0RAU4-0TN05'    

    #
    # Create VDS for Performance and PG
        $vdsname = 'VDS_Performance'
        $portGroup = 'VDS_Performance_pg'

        # set  MTU 9000 as this VDS does not have uplinks to the network
        
        createVDS $dataCenter  $vdsname 9000 0
   
        createVDSPG $dataCenter $vdsname $portGroup 12

        $esxHost = 'esx-perf.corp.local'
        addHostToVDS $esxHost $vdsname
        #Start-Sleep 20 
    
        createVDS $dataCenter 'VDS_vertical_scale' 8128 1
	    createVDSPG $dataCenter 'VDS_vertical_scale' 'VDS_vertical_scale_pg' 128
        addHostToVDS $esxHost 'VDS_vertical_scale' 
        #Start-Sleep 60
    
        addVmnicToVDS $esxHost 'VDS_vertical_scale' 'vmnic1'
    # Scan for storage
    scanStorage $esxHost

    #
    # Validate all the data stores are present.
    $resultsx=$false
    validateEsxPerfDataStore ([Ref]$resultsx)
    if($resultsx -eq $false) {
        Write-Host -BackgroundColor White -ForegroundColor Red "Data store validation failed on $esxHost - Please chek for logs"
    } else {

        Write-Host -ForegroundColor Green "Data store validation passed on $esxHost "
    }

    Write-Host -ForegroundColor Green "Performance and Vertical State Infrastructure preperation DONE"
    Write-Host -ForegroundColor White "Check messages for errors or warnings"

}

Function readyPerfInfra() {
    # Move the IXIA VMS to VDS_performance_pg
    moveVMPG 'Ixia_card_1' 'ixia_standadr_sw_2' 'VDS_Performance_pg'
    moveVMPG 'Ixia_card_2' 'ixia_standadr_sw_2' 'VDS_Performance_pg'
    moveVMPG 'Ixia_card_3' 'ixia_standadr_sw_2' 'VDS_Performance_pg'
    moveVMPG 'Ixia_card_4' 'ixia_standadr_sw_2' 'VDS_Performance_pg'
    moveVMPG 'Ixia_card_5' 'ixia_standadr_sw_2' 'VDS_Performance_pg'
    moveVMPG 'Ixia_card_6' 'ixia_standadr_sw_2' 'VDS_Performance_pg'

    # Power on the IXIA
    powerOnIxia
}

# This will move IXIA to original infra and switch off
Function powerOffPerfInfra() {

    # Power on the IXIA
    shutDownIxia
    Write-Host "Sleeping for 30 Seconds to give time to IXIA to go down"
    [Console]::Out.Flush() 
    Start-Sleep 30

    # Move the IXIA VMS to VDS_performance_pg
    moveVMPG 'Ixia_card_1' 'VDS_Performance_pg' 'ixia_standadr_sw_2' 
    moveVMPG 'Ixia_card_2' 'VDS_Performance_pg' 'ixia_standadr_sw_2' 
    moveVMPG 'Ixia_card_3' 'VDS_Performance_pg' 'ixia_standadr_sw_2' 
    moveVMPG 'Ixia_card_4' 'VDS_Performance_pg' 'ixia_standadr_sw_2' 
    moveVMPG 'Ixia_card_5' 'VDS_Performance_pg' 'ixia_standadr_sw_2' 
    moveVMPG 'Ixia_card_6' 'VDS_Performance_pg' 'ixia_standadr_sw_2'
    
}
##
# This is highly customized function for esxPerf
# We comment out SVM_Data_store_1 as we may not need
# If we start using then please uncomment
##
Function validateEsxPerfDataStore([Ref]$results) {
    $resultsx = $false
    checkDataStores 'esx-perf.corp.local' 'VM-DataStore' ([Ref]$resultsx)
    if($resultsx -eq $false) {
        Write-Host -BackgroundColor White -ForegroundColor Red "Unable to Find DataStore VM-DataStore"
        $results.value = $false
    }
    checkDataStores 'esx-perf.corp.local' 'datastore1' ([Ref]$resultsx)
    if($resultsx -eq $false) {
        Write-Host -BackgroundColor White -ForegroundColor Red "Unable to Find DataStore datastore1"
        $results.value = $false
    }
   # checkDataStores 'esx-perf.corp.local' 'SVM_datastore_1' ([Ref]$resultsx)
   # if($resultsx -eq $false) {
   #     Write-Host -BackgroundColor White -ForegroundColor Red "Unable to Find DataStore SVM_datastore_1"
   #     $results.value = $false
   # }
    $results.value = $true

}

Function prepareVerticalScale([int]$start, [int]$end) {

# Move the VMs to esx-perf
    registerLinuxVMs 'esx-perf.corp.local' '[VM-DataStore]' $start $end

   # Give a little sleep
   Write-Host "start Sleeping 60 seconds"
   [Console]::Out.Flush() 
   Start-Sleep 60

# Move the VMs to vertical_scale_pg
   

   for($num=$start; $num -le $end; $num++) {
      $vm = Get-VM "Linux-VM$num"
      $nw = Get-NetworkAdapter $vm
      Set-NetworkAdapter $nw -NetworkName  'VDS_vertical_scale_pg' -Confirm:$false -StartConnected:$true -RunAsync
   }
    

}

Function powerOnLinuxVM([int]$start, [int]$end) {
  for($num=$start; $num -le $end; $num++) {
      $vm = "Linux-VM$num"
      powerOnVM($vm)
      
   }

   # now answer the Questions , we do this trick here after the loop
   # it takes few minuets for the VM to get power on and questions avalable
   
   Write-Host "Start sleeping 60 seconds"
   [Console]::Out.Flush() 
   Start-Sleep 60

   for($num=$start; $num -le $end; $num++) {
      $vm_ = Get-VM "Linux-VM$num"
      $ques_ = Get-VMQuestion $vm_
      if($ques_) {
        #Get-VM "Linux-VM$num" | Get-VMQuestion | Set-VMQuestion -Option "button.uuid.copiedTheVM" -Confirm:$false
        Get-VM "Linux-VM$num" | Get-VMQuestion | Set-VMQuestion -DefaultOption -Confirm:$false
      }
   }

}

Function deleteLinuxVMs([int]$start, [int]$end) {
  for($num=$start; $num -le $end; $num++) {
      $vm = "Linux-VM$num"
      deleteVM $vm $false
      
   }

}

Function shutDownLinuxVMs([int]$start, [int]$end) {
  for($num=$start; $num -le $end; $num++) {
      $vm = "Linux-VM$num"
      #shutDownVM $vm
      powerOffVM $vm
      
   }

}

Function clearInfraConfig([string] $perfClusterName) {

  Get-VDSwitch -Name 'VDS_vertical_scale' | Remove-VDSwitch -Confirm:$false
  Get-VDSwitch -Name 'VDS_Performance' | Remove-VDSwitch -Confirm:$false

  # Put the esx host to maintanence
  Get-VMHost -Name esx-perf.corp.local | Set-VMHost -State Maintenance
 
  # remove from vCenter
  Remove-VMHost esx-perf.corp.local -Confirm:$false
 
  # remove cluster
  deleteClusterFromVC $perfClusterName

  Write-Host -ForegroundColor GREEN "Removed ESXi host esx-perf.corp.local from vCenter"

}
##
# Example:
# $networkName=VDS_vertical_scale_pg'
# Note: If you want total of n interfaces consider how many there
# and pass n -x to be added so we have total of n
#
##
Function AddInterfacesToLinuxVM([int]$start, [int]$end, [int] $numOfInf, [string] $networkName) {

   if($numOfInf -gt 10) {
    write-Host -ForegroundColor Magenta "$numOfInf is greater than maximum 10 specified by vSphere"
    return
   }

   $pg = Get-VDPortgroup -Name $networkName -ErrorAction SilentlyContinue
   if($pg -eq $null) {
    write-Host -ForegroundColor Magenta "$networkName does not exist can not proceed"
    return

   }
   for($num=$start; $num -le $end; $num++) {
      $vm = Get-VM "Linux-VM$num" -ErrorAction SilentlyContinue
      #$nw = Get-NetworkAdapter $vm
      if($vm) {
          for($nn=1; $nn -le $numOfInf; $nn++) { 
            New-NetworkAdapter "Linux-VM$num" -PortGroup  $networkName -Confirm:$false -StartConnected:$true
          }
      } else {
         write-Host -ForegroundColor Magenta ""Linux-VM$num" Does not exsist"
      }
   }
    

}


Function getPrimaryIntf([System.IO.Stream]$stream, [Ref] $primaryIntf){
    $stream.WriteLine("ifconfig -s")
    sleep -seconds 10
    $result = $stream.Read()
    $r=$result.Split([Environment]::NewLine) 
    foreach ($line  in $r) {
        #Write-Host "$line"
        $entry = $line.Split(' ')
        if($entry[0].Contains('ens') ) {
            $inf = $entry[0]
            write-Host -ForegroundColor Green "$inf Primary Interface found"
            $primaryIntf.value = $inf
            return
        }
        
    }  
    Write-Host "Primary interface not found"
    
}

Function getInterfaces([System.IO.Stream]$stream, [String]$primaryIntf, [System.Object] $otherIntf1) {

    if($primaryIntf -eq $null) {
        Write-Host -ForegroundColor Red "No primary interface specified can not proceed"
        return
    }
    $stream.WriteLine("ifconfig -a -s")
    sleep -seconds 10
    $result = $stream.Read()
    $r=$result.Split([Environment]::NewLine) 
    foreach ($line  in $r) {
        #Write-Host "$line"
        $entry = $line.Split(' ')
        if($entry[0].Contains('ens') ) {
            $inf = $entry[0]
            if($inf -ne $primaryIntf) {
                write-Host -ForegroundColor Green "$inf Interface found"
                $otherIntf1.Add($inf)
            }
            
        }
        
    }  
    return
}

Function configInterfaceIP([System.IO.Stream]$stream, [System.Object] $otherIntf, [int]$hostid) {

    for($num=0; $num -lt $otherIntf.count; $num++) {
        $if = $otherIntf[$num]
        $cardid = $num + 1
        $cmd  = "ifconfig $if 172.20.$cardid.$hostid netmask 255.255.255.0"
        $stream.WriteLine( $cmd )
        
    }

    #
    # Read at the end to clear the buffer
    #
    Sleep -s 2
    $x=$stream.Read()
    #Write-Host " Response $x "

}
#PowerShell Dictionary
$oddIP = @{1='172.16.11.1';255='172.16.11.2';256='172.16.11.3'}

Function getIPAddress([int] $id, [Ref] $ipAddress) {
    if(($id -gt 256) -or ($id -lt 0)){
        return
    }
    if($oddIP.Contains($id)) {
        $ipAddress.Value = $oddIP.Item($id)
    } else {
        $ipAddress.Value = "172.16.10.$num"
    }
}

###
# IP addresses are assigned 172.20.<cardid>.<hostid>
# we use class C subnet here for each card id (network card)
# e.g. network card 2 of all the host will have 172.20.2. address
# e.g . network card 3 of all the hosts will have 172.20.3 address
# network card one is the primary interface and it has 172.16.10/23 address 
# space please consult documentation for those addresses
#
####
Function connectAndAddIP([int]$startid, [int]$endid) {
    for($num=$startid; $num -le $endid; $num++) {
        $linuxHostIP=$null
         
        getIPAddress $num ([Ref]$linuxHostIP)
        if($linuxHostIP -eq $null) {
            Write-Host -ForegroundColor Red "Unable to find IP address of ID $num"
            return
        }
        $ssh = New-SSHSession -ComputerName $linuxHostIP -Credential $mycreds -AcceptKey  -Force -ErrorAction SilentlyContinue
        if($ssh -eq $null) {
            Write-Host -ForegroundColor Yellow "Establishing SSH to Host $linuxHostIP failed.. Sleep 60 secs and retry "
            [Console]::Out.Flush() 
            Start-Sleep 60
            Write-Host -ForegroundColor Yellow "SSH to Host $linuxHostIP connection retrying "
            $ssh = New-SSHSession -ComputerName $linuxHostIP -Credential $mycreds -AcceptKey  -Force -ErrorAction SilentlyContinue
            if($ssh -eq $null) {
                Write-Host -ForegroundColor red "Establishing SSH to Host $linuxHostIP failed.. again giving up "
                return

            }

        }
        Write-Host -ForegroundColor Green "Sucessfully Established connection to $linuxHostIP"

        $stream = $ssh.Session.CreateShellStream("PS-SSH", 0, 0, 0, 0, 1000)
        $result = Invoke-SSHStreamExpectSecureAction -ShellStream $stream -Command "sudo su -" -ExpectString "[sudo] password for $($sUser):" -SecureAction $secpasswd
        if($result -eq $false) {
            Write-Host -ForeGround Cyan "Connection to Host $linuxHostIP (Linux-VM$num) Failed"
            return
        }
        $intf=$null
        getPrimaryIntf $stream ([Ref]$intf)
        #
        # Give a delay and try one more time
        if($intf -eq $null) {
            Write-Host -ForegroundColor Red "Primary interface not present and Trying again giving 60 sec delay"
            Start-Sleep -Seconds 60
            getPrimaryIntf $stream ([Ref]$intf)
        }
        
        if($intf -eq $null) {
            Write-Host -ForegroundColor Red "Primary interface not found can not proceed"
            return
        }
        #
        # Arrays are always passed as reference
        $otherIntf = New-Object System.Collections.ArrayList
        getInterfaces $stream $intf $otherIntf
        #Write-Host $otherIntf

        configInterfaceIP $stream $otherIntf  $num
        $stream.Close()
        Remove-SSHSession $ssh
        Write-Host -ForegroundColor Green "Configured IP addresses for host $linuxHostIP"

        
    }

}

##
# Below captured all the historical tests. That were used duruing development
# you may uncomment and use them if needed.
#
##
Function HistoricalTests() {
    #addHostToVC 'esx-perf.corp.local' 'perfCluster' 'root' 'VMware1!' '4N20N-QYN9Q-L8F8T-0RAU4-0TN05'
    #createVDS  'Cert-DC' 'T1' 8128 0
    #createVDSPG 'Cert-DC' 'T1' 'newPG'
    #addVmnicToVDS 'esx-perf.corp.local' 'T1' 'vmnic2'
    #addHostToVDS 'esx-perf.corp.local' 'T1'
    #moveVMPG 'Ixia_card_1' 'ixia_standadr_sw_2' 'vDS_Performance_pg'
    #powerOnVM 'Ixia_card_1'
    #powerOnIxia
    # shutDownVM 'Ixia_card_1'
    #shutDownIxia
    #deleteVM 'Ixia_card_1'
    ##scanStorage 'esx-perf.corp.local'
    ## create datastorage
    ## add LinuxVM
    ##Show-Menu 'Performance and Scale'
    #$resultsx = $false

    #validateEsxPerfDataStore([Ref]$resultsx)
    #if ($resultsx -eq $true) {
    #    Write-Host "True all datastores are in order"
    #} else {
    #    Write-Host "False some datastores are missing please check output"
    #}

    #Write-Host "Check DS $checkds $resultsx"
    #Select-Choice
    #prepareInfra 
    #Select-Choice

    #AddInterfacesToLinuxVM 1 2 4 'VDS_vertical_scale_pg'
}
connectToVC 'vcsa-02a.corp.local' 'administrator@corp.local' 'VMware1!'

Select-Choice
disconnectFromVC('vcsa-02a.corp.local')