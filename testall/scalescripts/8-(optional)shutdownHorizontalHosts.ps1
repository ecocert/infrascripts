Add-PSSnapin vmware.vimautomation.core
For ( $num=1;$num -lt 33;$num++) {
    connect-viserver -server esx-horizontal-$num.corp.local -User root -Password VMware1!
    connect-viserver -server esx-horizontal-$num-1.corp.local -User root -Password VMware1!
    $currentesxhost = Get-VMHost esx-horizontal-$num.corp.local
    #Stop-VMHost esx-horizontal-$num.corp.local -Confirm
    $currentesxhost | Foreach {Get-View $_.ID} | Foreach {$_.ShutdownHost_Task($TRUE)}
    $currentesxhost = Get-VMHost esx-horizontal-$num-1.corp.local
    #Stop-VMHost esx-horizontal-$num-1.corp.local -Confirm:$false
    $currentesxhost | Foreach {Get-View $_.ID} | Foreach {$_.ShutdownHost_Task($TRUE)}
}