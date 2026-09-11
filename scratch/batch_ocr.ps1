Add-Type -AssemblyName System.Drawing
[Windows.Globalization.Language, Windows.Foundation.Globalization, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation.Ocr, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new("en-US"))

function Get-OcrText($imagePath) {
    $fileTask = [Windows.Storage.StorageFile]::GetFileFromPathAsync($imagePath)
    $file = $fileTask.GetAwaiter().GetResult()
    $streamTask = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read)
    $stream = $streamTask.GetAwaiter().GetResult()
    $decoderTask = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
    $decoder = $decoderTask.GetAwaiter().GetResult()
    $bitmapTask = $decoder.GetSoftwareBitmapAsync()
    $bitmap = $bitmapTask.GetAwaiter().GetResult()
    $ocrResultTask = $engine.RecognizeAsync($bitmap)
    $ocrResult = $ocrResultTask.GetAwaiter().GetResult()
    
    $lines = @()
    foreach ($line in $ocrResult.Lines) {
        $lines += $line.Text
    }
    return $lines
}

for ($i = 1; $i -le 12; $i++) {
    $num = $i.ToString("00")
    $imgPath = Join-Path (Get-Location) "scratch\pdf_pages\page_$num.png"
    $lines = Get-OcrText $imgPath
    $outPath = Join-Path (Get-Location) "scratch\pdf_pages\page_$num.txt"
    $lines | Set-Content -Path $outPath -Encoding UTF8
    Write-Host "Processed page_$num.png -> $($lines.Count) lines"
}
