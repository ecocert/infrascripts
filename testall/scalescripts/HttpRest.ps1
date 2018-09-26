

$server="172.17.11.11"
$NSXuri = "https://$server"
$user = "admin"
$pass = "VMware1!"
$pair = "${user}:${pass}"

$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)

$basicAuthValue = "Basic $base64"


# Small Function to execute a REST operations and return the JSON response
function http-rest-json
{
  <#
  .SYNOPSIS
    This function establishes a connection to the NSX API
  .DESCRIPTION
    This function establishes a connection to  NSX API
  .PARAMETER method
    Specify the REST Method to use (GET/PUT/POST/DELETE)"
  .PARAMETER uri
    Specify the REST URI that identifies the resource you want to interact with
  .PARAMETER body
    Specify the body content if required (PUT/POST)
  .INPUTS
    String: REST Method to use.
    String: URI that identifies the resource
    String: Body if required
  .OUTPUTS
    JsonObject: Request result in JSON
  .LINK
    None.
  #>

  [CmdletBinding()]
  param(
    [
      parameter(
        Mandatory = $true,
        HelpMessage = "Specify the REST Method to use (GET/PUT/POST/DELETE)",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $method,
    [
      parameter(
        Mandatory = $true,
        HelpMessage = "Specify the REST URI that identifies the resource you want to interact with",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $uri,
    [
      parameter(
        Mandatory = $false,
        HelpMessage = "Specify the body content if required (PUT/POST)",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $body = $null
  )

  Begin {
    # Build Url from supplied uri parameter
    $Url = $NSXuri + $uri
  }

  Process {
    # Construct headers with authentication data + expected Accept header (xml / json)
   $headers = @{Authorization = $basicAuthValue;Accept='application/json'}


    # Build Invoke-RestMethod request
    try
    {
      if (!$body) {
        $HttpRes = Invoke-RestMethod -Uri $Url -Method $method -Headers $headers
      }
      else {
        $HttpRes = Invoke-RestMethod -Uri $Url -Method $method -Headers $headers -Body $body -ContentType "application/json"
      }
    }
    catch {
      Write-Host -ForegroundColor Red "Error connecting to $Url"
      Write-Host -ForegroundColor Red $_.Exception.Message
    }

    # If the response to the HTTP request is OK,
    # Convert it to JSON before returning it.
    if ($HttpRes) {
      $json = $HttpRes | ConvertTo-Json
      return $json
    }
    else {
      Write-Host -ForegroundColor Red "Error retrieving response body for $Url"
    }
  }
  End {
      # What to do here ?
  }
}

# Small Function to execute a REST operations and return the JSON response
function http-rest-xml
{
  <#
  .SYNOPSIS
    This function establishes a connection to the NSX API
  .DESCRIPTION
    This function establishes a connection to  NSX API
  .PARAMETER method
    Specify the REST Method to use (GET/PUT/POST/DELETE)"
  .PARAMETER uri
    Specify the REST URI that identifies the resource you want to interact with
  .PARAMETER body
    Specify the body content if required (PUT/POST)
  .INPUTS
    String: REST Method to use.
    String: URI that identifies the resource
    String: Body if required
  .OUTPUTS
    JsonObject: Request result in JSON
  .LINK
    None.
  #>

  [CmdletBinding()]
  param(
    [
      parameter(
        Mandatory = $true,
        HelpMessage = "Specify the REST Method to use (GET/PUT/POST/DELETE)",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $method,
    [
      parameter(
        Mandatory = $true,
        HelpMessage = "Specify the REST URI that identifies the resource you want to interact with",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $uri,
    [
      parameter(
        Mandatory = $false,
        HelpMessage = "Specify the body content if required (PUT/POST)",
        ValueFromPipeline = $false
      )
    ]
    [String]
    $body = $null
  )

  Begin {
    # Build Url from supplied uri parameter
    $Url = $NSXuri + $uri
  }

  Process {
    # Construct headers with authentication data + expected Accept header (xml / json)
  
    $headers = @{Authorization = $basicAuthValue;Accept='application/xml'}

    # Build Invoke-RestMethod request
    try
    {
      if (!$body) {
        $HttpRes = Invoke-RestMethod -Uri $Url -Method $method -Headers $headers
      }
      else {
        $HttpRes = Invoke-RestMethod -Uri $Url -Method $method -Headers $headers -Body $body -ContentType "application/xml"
      }
    }
    catch {
      Write-Host -ForegroundColor Red "Error connecting to $Url"
      Write-Host -ForegroundColor Red $_.Exception.Message
    }

    # If the response to the HTTP request is OK,
    if ($HttpRes) {
      return $HttpRes
    }
  }
  End {
      # What to do here ?
  }
}
