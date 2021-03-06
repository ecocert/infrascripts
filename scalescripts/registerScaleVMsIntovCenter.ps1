param($start,$end) 
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
 



 Function registerLinuxVMs([string] $VMXDataStore, [int] $StartNumOfVM, [int] $endNumOfVM) {



    For ( $num=$StartNumOfVM;$num -le $endNumOfVM;$num++) { 
    
    

   
   
        $VMXFile = "$VMXDataStore Tiny-Linux-VM-$num/Tiny-Linux-VM-$num.vmx"
        $ESXHost = "esx-scale-$num.corp.local"
  
        $newVM = New-VM -VMFilePath $VMXFile -VMHost $ESXHost -RunAsync -ErrorAction SilentlyContinue
        if($newVM -eq $null) {
            Write-Host -ForegroundColor DarkRed "VM Tiny-Linux-VM-$num was not added due to error"
        } else {
            Write-Host -ForegroundColor GREEN "added VM $VMXFile to host $ESXHost"
        }
    } 


}

 registerLinuxVMs  '[VM-DataStore]' $start $end

Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false