param($start,$end) 
Add-PSSnapin vmware.vimautomation.core


connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

For ( $num=$start;$num -le $end;$num++) { 
#scan the new VMFS storage for each of the ESXi Scale host
$vmhost = get-vmhost esx-scale-$num.corp.local

$vmhost| Get-VMHostStorage -RescanAllHBA -RescanVmfs
}
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false