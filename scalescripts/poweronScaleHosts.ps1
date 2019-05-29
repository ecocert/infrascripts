param($start,$end) 
Add-PSSnapin vmware.vimautomation.core



#Amount of time to wait (in seconds) between each start list of VMs
$FinalWaitTime = "300"


For ( $num=1;$num -le 25;$num++) {
    connect-viserver -server esx-horizontal-$num.corp.local -User root -Password VMware1!
    connect-viserver -server esx-horizontal-$num-1.corp.local -User root -Password VMware1!
} 


$vms = New-Object System.Collections.Arraylist
$index=0
For($vmcount=$start;$vmcount -le $end;$vmcount++)
{
    $vm = Get-VM "esx-scale-$vmcount"
    $vms.Insert($index,$vm)
    $index++;
    
}
Write "vms list to power on is $vms"
Start-VM -VM  $vms  -Confirm:$False

Write "`n $(Get-Date) Please wait for $FinalWaitTime more Seconds for started VMs to stabilize.After that add them into vCenter"

For ( $num=1;$num -le 25;$num++) {
    Disconnect-VIServer -server esx-horizontal-$num.corp.local -confirm:$false
    Disconnect-VIServer -server esx-horizontal-$num-1.corp.local -confirm:$false
} 

