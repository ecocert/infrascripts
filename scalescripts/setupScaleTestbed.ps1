﻿function Show-Menu
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
                $ScriptToRun= $ScriptPath+"poweronScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
                #&$ScriptToRun
           } '3' {
                
                'You chose option #3'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"addScaleHostsIntovCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '4' {
                
                'You chose option #4'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $ScriptToRun= $ScriptPath+"registerScaleVMsIntovCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           }'5' {
                
                'You chose option #5'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"addScaleHostsToVDS.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '6' {
                
                'You chose option #6'
                write-Host "There are 4 FREENAS Servers with the following index-IP mapping,`n 1-192.168.110.61, 2-192.168.110.62, 3-192.168.110.63, 4-192.168.110.64"
                $start = read-host "Please enter the start FREENAS Server index"
                $end = read-host "Please enter the end FREENAS Server index"
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
                
           }'7' {
                
                'You chose option #7'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"storageScanOnScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           
           } '8' {
                
                'You chose option #8'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"removeScaleHostsFromVDS.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           }'9' {
                
                'You chose option #9'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $ScriptToRun= $ScriptPath+"unregisterVMsFromvCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '10' {
                
                'You chose option #10'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"removeScaleHostsFromvCenter.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '11' {
                
                'You chose option #11'
                write-Host "There are 1..256 esx scale hosts"
                $start = read-host "Please enter the start esx scale host number"
                $end = read-host "Please enter the end esx scale host number"
                $ScriptToRun= $ScriptPath+"shutdownScaleHosts.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '12' {
                
                'You chose option #12'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $ScriptToRun= $ScriptPath+"powerOnLinuxVMs.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } '13' {
                
                'You chose option #13'
                write-Host "There are 1..256 Linux VMs"
                $start = read-host "Please enter the start Linux VM number"
                $end = read-host "Please enter the end Linux VM number"
                $ScriptToRun= $ScriptPath+"shutdownLinuxVMs.ps1 -start $start -end $end"
                Invoke-Expression $ScriptToRun
           } 'q' {
                return
           }
     }
     pause
}
until ($input -eq 'q')