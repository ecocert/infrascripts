param($start,$end)
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
 
########################################################################
# Remove Multiple Hosts from vCenter
######################################################################## 
 
 
#Remove Scale hosts from vCenter
For ( $num=$start;$num -le $end;$num++) { 
 
 Get-VMHost -Name esx-scale-$num.corp.local | Set-VMHost -State Maintenance
 Remove-VMHost esx-scale-$num.corp.local -Confirm:$false
 
 Write-Host -ForegroundColor GREEN "Removed ESXi host esx-scale-$num.corp.local from vCenter"
} 
Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false
# End Script 