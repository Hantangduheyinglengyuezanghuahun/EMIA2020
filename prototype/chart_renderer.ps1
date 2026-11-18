# Render two email-safe PNG charts using Windows' built-in drawing library.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$outputs = @{}
function Colour($hex) { [System.Drawing.ColorTranslator]::FromHtml($hex) }
function Text($value, $x, $y, $size = 23, $hex = '#334155') {
    $family = if ($payload.font) { $payload.font } else { 'Arial' }
    if ($payload.translations) {
        $entry = $payload.translations.PSObject.Properties[[string]$value]
        if ($entry) { $value = $entry.Value } else { $value = ([string]$value).Replace(' to ', ' - ') }
    }
    $font = [System.Drawing.Font]::new($family, [single]$size, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
    $brush = [System.Drawing.SolidBrush]::new((Colour $hex))
    try { $g.DrawString([string]$value, $font, $brush, [single]$x, [single]$y) }
    finally { $font.Dispose(); $brush.Dispose() }
}
function Box($x, $y, $width, $height, $hex) {
    $brush = [System.Drawing.SolidBrush]::new((Colour $hex))
    try { $g.FillRectangle($brush, [single]$x, [single]$y, [single]$width, [single]$height) }
    finally { $brush.Dispose() }
}
function Line($x1, $y1, $x2, $y2, $hex, $width = 3, $dashed = $false) {
    $pen = [System.Drawing.Pen]::new((Colour $hex), [single]$width)
    if ($dashed) { $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }
    try { $g.DrawLine($pen, [single]$x1, [single]$y1, [single]$x2, [single]$y2) }
    finally { $pen.Dispose() }
}
foreach ($kind in @('glucose', 'food')) {
    $height = if ($kind -eq 'glucose') { 720 } else { 480 }
    $bitmap = [System.Drawing.Bitmap]::new(1200, $height)
    $g = [System.Drawing.Graphics]::FromImage($bitmap)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear([System.Drawing.Color]::White)
    try {
        if ($kind -eq 'glucose') {
            Text 'GLUCOSE HISTORY + CURRENT ESTIMATE + FORECAST' 30 12 30 '#142D48'
            Text 'mg/dL' 30 52 20
            $minX = [double]$payload.min_x
            $maxX = [double]$payload.max_x
            $maxY = [double]$payload.max_y
            function Px($value) { 90 + 1050 * ([double]$value - $minX) / ($maxX - $minX) }
            function Py($value) { 500 - 390 * [double]$value / $maxY }
            for ($i = 0; $i -le 4; $i++) {
                $value = $i * $maxY / 4
                $y = Py $value
                Line 90 $y 1140 $y '#E2E8F0' 1
                Text ([math]::Round($value)) 24 ($y - 18) 28
            }
            foreach ($reference in @(70, 180)) {
                $y = Py $reference
                Line 90 $y 1140 $y '#CBD5E1' 2 $true
            }
            $forecast = @($payload.forecast)
            $polygon = [System.Collections.Generic.List[System.Drawing.PointF]]::new()
            foreach ($point in $forecast) { $polygon.Add([System.Drawing.PointF]::new((Px $point.x), (Py $point.high))) }
            for ($i = $forecast.Count - 1; $i -ge 0; $i--) { $polygon.Add([System.Drawing.PointF]::new((Px $forecast[$i].x), (Py $forecast[$i].low))) }
            if ($polygon.Count -ge 3) {
                $brush = [System.Drawing.SolidBrush]::new((Colour '#EDE5FF'))
                try { $g.FillPolygon($brush, $polygon.ToArray()) } finally { $brush.Dispose() }
            }
            $points = @($payload.measured)
            for ($i = 1; $i -lt $points.Count; $i++) {
                Line (Px $points[$i-1].x) (Py $points[$i-1].y) (Px $points[$i].x) (Py $points[$i].y) '#167D8D' 4
            }
            foreach ($point in $points) {
                $brush = [System.Drawing.SolidBrush]::new((Colour '#167D8D'))
                try { $g.FillEllipse($brush, [single]((Px $point.x)-5), [single]((Py $point.y)-5), 10, 10) } finally { $brush.Dispose() }
            }
            if ($points.Count -gt 0) {
                $point = $points[-1]
                Text ([string]$point.y) ([math]::Min(1040, (Px $point.x)+8)) ([math]::Max(65, (Py $point.y)-32)) 24 '#245FE8'
            } else { Text 'No measured history supplied' 100 120 24 '#AD6600' }
            for ($i = 1; $i -lt $forecast.Count; $i++) {
                Line (Px $forecast[$i-1].x) (Py $forecast[$i-1].y) (Px $forecast[$i].x) (Py $forecast[$i].y) '#8055CF' 4 $true
            }
            foreach ($point in $forecast) { Text ([string]$point.y) ((Px $point.x)-16) ((Py $point.y)-40) 30 '#8055CF' }
            $estimate = $payload.current_estimate
            $estimateX = Px $estimate.x
            Line $estimateX (Py $estimate.low) $estimateX (Py $estimate.high) '#8055CF' 4
            Line ($estimateX-12) (Py $estimate.low) ($estimateX+12) (Py $estimate.low) '#8055CF' 4
            Line ($estimateX-12) (Py $estimate.high) ($estimateX+12) (Py $estimate.high) '#8055CF' 4
            $brush = [System.Drawing.SolidBrush]::new((Colour '#8055CF'))
            try { $g.FillEllipse($brush, [single]($estimateX-8), [single]((Py $estimate.y)-8), 16, 16) } finally { $brush.Dispose() }
            Line $estimateX (Py $estimate.y) (Px $forecast[0].x) (Py $forecast[0].y) '#8055CF' 4 $true
            Text ('Estimate now: ' + $estimate.y) ([math]::Max(95, $estimateX-250)) 80 28 '#8055CF'
            $nowX = Px $payload.now
            Line $nowX 78 $nowX 500 '#64748B' 2 $true
            Text 'NOW' ([math]::Min(1070, $nowX+6)) 58 19 '#64748B'
            foreach ($tick in $payload.ticks) { Text $tick.label ([math]::Min(1000, [math]::Max(70, (Px $tick.x)-58))) 520 28 }
            Text $payload.reading_label 90 605 28 '#167D8D'
            Text 'Dashed: demo future forecast' 600 605 28 '#8055CF'
            Text 'Shading / whisker: illustrative ranges (not validated)' 90 655 28 '#8055CF'
        } else {
            Text 'FOOD ESTIMATES - SIMULATED' 30 12 26 '#142D48'
            Text 'Estimated grams and illustrative uncertainty ranges' 30 55 22
            $scale = 850 / [double]$payload.food_max
            $row = 0
            foreach ($item in $payload.food) {
                $top = 112 + $row * 140
                Text ($item.label + ': ' + $item.estimate + ' g') 35 $top 27 '#142D48'
                Box 35 ($top+47) 850 30 '#F1F5F9'
                Box 35 ($top+47) ($item.estimate*$scale) 30 $item.color
                Line (35+$item.low*$scale) ($top+91) (35+$item.high*$scale) ($top+91) '#64748B' 3
                Line (35+$item.low*$scale) ($top+83) (35+$item.low*$scale) ($top+99) '#64748B' 3
                Line (35+$item.high*$scale) ($top+83) (35+$item.high*$scale) ($top+99) '#64748B' 3
                Text ($item.low.ToString() + ' to ' + $item.high + ' g') 915 ($top+45) 23
                $row++
            }
            Text 'Sugar is included in total carbohydrates; do not add the two bars.' 35 420 22 '#64748B'
        }
        $stream = [System.IO.MemoryStream]::new()
        try {
            $bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
            $outputs[$kind] = [Convert]::ToBase64String($stream.ToArray())
        } finally { $stream.Dispose() }
    } finally { $g.Dispose(); $bitmap.Dispose() }
}
$outputs | ConvertTo-Json -Compress
