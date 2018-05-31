param([Int32]$start,[Int32]$end)
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

for($num=$start; $num -le $end; $num++) {
      $vm = "Tiny-Linux-VM-$num"
      $vmInfo = Get-VM -Name $vm
      #Shutdown-VMGuest -VM $vmInfo -Confirm:$false
      #$vminfo | Shutdown-VMGuest -Confirm:$false
      $vminfo | Stop-VMGuest -COnfirm:$false
      Write-Host -ForegroundColor GREEN " Shutdown $vm done"
}
      
