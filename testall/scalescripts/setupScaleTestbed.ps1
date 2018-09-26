function Show-Menu
{
     param (
           [string]$Title = 'Test bed setup for Horizontal Scale testing'
     )
     
     Write-Host "================ $Title ================"
     
     Write-Host "1: Press '1' for checking whether Horizontal hosts are in UP state"
     Write-Host "2: Press '2' for powering on the scale ESXi Hosts"
     Write-Host "3: Press '3' to add the scale hosts into vCenter"
     Write-Host "4: Press '4' to register Linux VMs into Scale Hosts in the vCenter"
     Write-Host "5: Press '5' to add the scale hosts into vDS and migrate Linux VM network to VDS"
     Write-Host "6: Press '6' to perform storage volume, extent and target creation in the FREENAS Servers"
     Write-Host "7: Press '7' to do the storage scan on the scale hosts"
     Write-Host "8: Press '8' to remove scale hosts from vDS"
     Write-Host "9: Press '9' to unregister Linux VMs from vCenter"
     Write-Host "10: Press '10' to remove scale hosts from vCenter"
     Write-Host "11: Press '11' to shutdown scale hosts"
     Write-Host "12: Press '12' to power on linux VMs"
     Write-Host "13: Press '13' to shutdown linux VMs"
     Write-Host "14: Press '14' to Prepare Host Clusters for NSX"
     Write-Host "15: Press '15' to Deploy NSX Guest Introspection or Partner Service"
     Write-Host "16: Press '16' to Monitor and Resolve alarms raised in Guest Introspection or Partner Service deployment"

     Write-Host "Q: Press 'Q' to quit."
}

$PSScriptRoot 
$ScriptPath= $PSScriptRoot+"\"
do
{
     Show-Menu
     $input = Read-Host "Please make a selection"
     switch ($input)
     {
             '1' {
                
                'You chose option #1'
                $ScriptToRun= $ScriptPath+"pingHorizontalHosts.ps1"
                Invoke-Expression $ScriptToRun
                break;
                #&$ScriptToRun
           } '2' {
                
                'You chose option #2'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"poweronScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
                #&$ScriptToRun
           } '3' {
                
                'You chose option #3'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"addScaleHostsIntovCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '4' {
                
                'You chose option #4'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"registerScaleVMsIntovCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           }'5' {
                
                'You chose option #5'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"addScaleHostsToVDS.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '6' {
                
                'You chose option #6'
                write-Host "There are 4 FREENAS Servers with the following index-IP mapping,`n 1-192.168.110.61, 2-192.168.110.62, 3-192.168.110.63, 4-192.168.110.64"
                $start = read-host "Please enter the start FREENAS Server index"
                $end = read-host "Please enter the end FREENAS Server index"
                $time = Get-Date
                write-Host "Begin time $time"
                [int]$index=0
                for($index=$start; $index -le $end ; $index++)
                {
                    try
                    {
                        $ScriptToRun= $ScriptPath+"freeNASRestClient.ps1 -index $index"
                        Invoke-Expression $ScriptToRun
                    }
                    catch
                    {
                        write $_
                    }
                }
                $time = Get-Date
                Write-Host "End time $time"
                
           }'7' {
                
                'You chose option #7'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"storageScanOnScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           
           } '8' {
                
                'You chose option #8'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"removeScaleHostsFromVDS.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           }'9' {
                
                'You chose option #9'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"unregisterVMsFromvCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '10' {
                
                'You chose option #10'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"removeScaleHostsFromvCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '11' {
                
                'You chose option #11'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"shutdownScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '12' {
                
                'You chose option #12'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"powerOnLinuxVMs.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '13' {
                
                'You chose option #13'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $time = Get-Date
                write-Host "Begin time $time"
                $ScriptToRun= $ScriptPath+"shutdownLinuxVMs.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                $time = Get-Date
                Write-Host "End time $time"
           } '14' {
                
                'You chose option #14'
                write-Host "There are 4 clusters with the following index-IP mapping,`n 1-ScaleCluster1, 2-ScaleCluster2, 3-ScaleCluster3, 4-ScaleCluster4"
                $start = read-host "Please enter the start ScaleCluster index"
                $end = read-host "Please enter the end ScaleCluster index"
                $time = Get-Date
                write-Host "Begin time $time"
                [int]$index=0
                for($index=$start; $index -le $end ; $index++)
                {
                    try
                    {
                        $ScriptToRun= $ScriptPath+"NSXHostPreparationInstallation.ps1 -index $index"
                        Invoke-Expression $ScriptToRun
                        sleep 10
                        $ScriptToRun= $ScriptPath+"NSXHostPreparationStatus.ps1 -index $index"
                        Invoke-Expression $ScriptToRun
                    }
                    catch
                    {
                        write $_
                    }
                }
               
                $time = Get-Date
                Write-Host "End time $time"
           }'15' {
                
                'You chose option #15'
                write-Host "There are 4 clusters with the following index-IP mapping,`n 1-ScaleCluster1, 2-ScaleCluster2, 3-ScaleCluster3, 4-ScaleCluster4"
                $start = read-host "Please enter the start ScaleCluster index"
                $end = read-host "Please enter the end ScaleCluster index"
                $servicename = read-host 'Please enter the service name to be deployed with in quotes, for guest introspection type "Guest Introspection"'
                $time = Get-Date
                write-Host "Begin time $time"
                [int]$index=0
                for($index=$start; $index -le $end ; $index++)
                {
                    try
                    {
                        $ScriptToRun= $ScriptPath+"NSXServiceDeployment.ps1 -index $index -servicename $servicename"
                        Invoke-Expression $ScriptToRun
                        sleep 15
                        $ScriptToRun= $ScriptPath+"NSXServiceDeploymentStatus.ps1 -index $index -servicename $servicename"
                        Invoke-Expression $ScriptToRun
                    }
                    catch
                    {
                        write $_
                    }
                }
               
                $time = Get-Date
                Write-Host "End time $time"
           }'16' {
                
                'You chose option #16'
                write-Host "There are 4 clusters with the following index-IP mapping,`n 1-ScaleCluster1, 2-ScaleCluster2, 3-ScaleCluster3, 4-ScaleCluster4"
                $start = read-host "Please enter the start ScaleCluster index"
                $end = read-host "Please enter the end ScaleCluster index"
                $servicename = read-host 'Please enter the service name to be monitored with in quotes, for guest introspection type "Guest Introspection"'
                $time = Get-Date
                write-Host "Begin time $time"
                [int]$index=0
                for($index=$start; $index -le $end ; $index++)
                {
                    try
                    {
                        $ScriptToRun= $ScriptPath+"NSXServiceDeploymentStatus.ps1 -index $index -servicename $servicename"
                        Invoke-Expression $ScriptToRun
                    }
                    catch
                    {
                        write $_
                    }
                }
                $time = Get-Date
                Write-Host "End time $time"
           }'q' {
                return
           }
     }
     pause
}
until ($input -eq 'q')