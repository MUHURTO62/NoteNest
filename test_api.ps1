Write-Output "Testing NoteNest API Endpoints"
Write-Output ""

$endpoints = @(
    'http://127.0.0.1:8000/api/admin/semesters/',
    'http://127.0.0.1:8000/api/admin/faculty/',
    'http://127.0.0.1:8000/api/admin/questions/',
    'http://127.0.0.1:8000/api/admin/overview/'
)

Write-Output "=== API Tests ==="
foreach ($url in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        Write-Output "PASS: $url (Status: $($response.StatusCode))"
    } catch {
        Write-Output "FAIL: $url"
    }
}

Write-Output ""
Write-Output "=== Frontend Test ==="
try {
    $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/index.html' -UseBasicParsing -ErrorAction Stop
    Write-Output "PASS: Frontend index.html"
} catch {
    Write-Output "FAIL: Frontend index.html"
}

Write-Output ""
Write-Output "=== Database Test ==="
$dbPath = 'C:\Users\User\Documents\NoteNest\NoteNest\backend\db.sqlite3'
if (Test-Path $dbPath) {
    $size = (Get-Item $dbPath).Length / 1KB
    Write-Output "PASS: Database exists (Size: $([Math]::Round($size, 2)) KB)"
} else {
    Write-Output "FAIL: Database missing"
}
