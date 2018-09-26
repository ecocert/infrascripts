param([Int32]$start,[Int32]$end)
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
 

Function unregistervm([int] $StartNumOfVM, [int] $endNumOfVM)
{
  For ( $num=$StartNumOfVM;$num -le $endNumOfVM;$num++) { 
    $vm = get-VM Tiny-Linux-VM-$num
    
    Remove-VM -VM $vm -DeleteFromDisk:$false -Confirm:$false -RunAsync
    Write-Host -ForegroundColor GREEN "Unregistering VM: $vm"
 }
}

 unregistervm  $start $end


Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false