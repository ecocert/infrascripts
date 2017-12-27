param($start,$end)
Add-PSSnapin vmware.vimautomation.core

#Connect to all the horizontal hosts
For ( $num=1;$num -le 32;$num++) {
    connect-viserver -server esx-horizontal-$num.corp.local -User root -Password VMware1!
    connect-viserver -server esx-horizontal-$num-1.corp.local -User root -Password VMware1!
} 


$vms = New-Object System.Collections.Arraylist

$index=0;
For($num=$start;$num -le $end;$num++)
{
    
    $vm = Get-VM "esx-scale-$num"
    $vms.Insert($index,$vm)
    $index++;
    
}
Write "vms list is $vms"
Stop-VM -VM  $vms  -Confirm:$False

For ( $num=1;$num -le 32;$num++) {
    Disconnect-VIServer -server esx-horizontal-$num.corp.local -confirm:$false
    Disconnect-VIServer -server esx-horizontal-$num-1.corp.local -confirm:$false
} 