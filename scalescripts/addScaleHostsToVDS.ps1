param($start,$end)
Add-PSSnapin vmware.vimautomation.core

Import-Module VMware.VimAutomation.Vds

connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
$time = Get-Date
write-Host "Begin time $time"

#Input vDS name and vDS port group
$vDS_name = "vDS_Data"
$vDS_pg = "vDS_VM_pg"

#Add Scale hosts into vDS with uplink as "vmnic1"
For ( $num=$start;$num -le $end;$num++) {  
#Add to new DVSwitch and swing leg over
#$VMhostObj | Get-VMHostNetworkAdapter -Physical -Name "vmnic1" | Remove-VirtualSwitchPhysicalNetworkAdapter -Confirm:$false

$VMHost = "esx-scale-$num.corp.local"
$VMHostObj = Get-VMHost $VMHost
$VDSwitch = Get-VDSwitch -Name $vDS_name
$VDSwitch |  Add-VDSwitchVMHost -VMHost $VMHost -Confirm:$false

#Get physical adapter to move
$vmhostadapter = $VMHostObj | Get-VMHostNetworkAdapter -Physical -Name vmnic1  
$VDSwitch | Add-VDSwitchPhysicalNetworkAdapter -VMHostNetworkAdapter $vmhostadapter -Confirm:$false
}


# Migrate Linux Guest VMs from "VM Network" to "vDC_VM_pg"
For($num=$start;$num -le $end;$num++) {
    
    $vm="Tiny-Linux-VM-$num"
    Get-NetworkAdapter $vm | %{
    Write-Host "Setting Network portgroup to" $vDS_pg on $vm
    $_ | Set-NetworkAdapter -PortGroup (Get-VDPortGroup -Name $vDS_pg -VDSwitch $vDS_name) -Confirm:$false
    
    }
}
$time = Get-Date
Write-Host "End time $time"
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false