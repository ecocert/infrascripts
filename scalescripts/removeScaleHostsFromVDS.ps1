param($start,$end)
Add-PSSnapin vmware.vimautomation.core
Import-Module VMware.VimAutomation.Vds
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
 
########################################################################
# Remove Hosts from vDS
######################################################################## 


$vSS_pg="VM Network"
$vDS_pg = "vDS_VM_pg"
$vDS_name="vDS_Data"
 
# Migrate Guest VMs from "vDS_VM_pg" to "VM Network"
Get-VM |Get-NetworkAdapter |Where {$_.NetworkName -eq $vDS_pg } |Set-NetworkAdapter -NetworkName $vSS_pg -Confirm:$false

For($num=$start;$num -le $end;$num++) {

    Get-VDSwitch -Name $vDS_name | Remove-VDSwitchVMHost -VMHost esx-scale-$num.corp.local -Confirm:$false
}
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false