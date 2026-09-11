Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.WindowsRuntime

[Windows.Globalization.Language, Windows.Foundation.Globalization, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation.Ocr, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null

$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.IsGenericMethod } | Select-Object -First 1

function Await($asyncOp, $type) {
    $asTask = $asTaskGeneric.MakeGenericMethod($type)
    $task = $asTask.Invoke($null, @($asyncOp))
    $task.Wait()
    return $task.Result
}

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new("en-US"))

for ($i = 1; $i -le 12; $i++) {
    $num = $i.ToString("00")
    $imgPath = (Resolve-Path "scratch\pdf_pages\page_$num.png").Path
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($imgPath)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $ocrResult = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    
    $lines = @()
    foreach ($line in $ocrResult.Lines) {
        $lines += $line.Text
    }
    $outPath = "scratch\pdf_pages\page_$num.txt"
    $lines | Set-Content -Path $outPath -Encoding UTF8
    Write-Host "Processed page_$num.png -> $($lines.Count) lines"
}
