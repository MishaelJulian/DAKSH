Add-Type -AssemblyName System.Drawing
[Windows.Globalization.Language, Windows.Foundation.Globalization, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation.Ocr, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new("en-US"))
Write-Host "OCR Engine Available: $($engine -ne $null)"
