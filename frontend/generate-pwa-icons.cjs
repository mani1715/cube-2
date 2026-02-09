#!/usr/bin/env node

/**
 * PWA Icon Generator Script
 * 
 * This script creates placeholder PWA icons in various sizes.
 * In production, replace these with actual branded icons using a proper icon generator.
 * 
 * Recommended tools for production icons:
 * - https://realfavicongenerator.net/
 * - https://www.pwabuilder.com/imageGenerator
 */

const fs = require('fs');
const path = require('path');

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const iconsDir = path.join(__dirname, 'public', 'pwa-icons');

// Create icons directory if it doesn't exist
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

// Create a simple SVG template
const createSVG = (size) => `
<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#6366F1;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" fill="url(#grad)" rx="${size * 0.15}"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${size * 0.4}" 
        font-weight="bold" fill="white" text-anchor="middle" dy=".35em">A</text>
</svg>
`;

// Create a simple HTML file that renders the SVG and converts to PNG
const createHTMLConverter = (size) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Icon Generator</title>
</head>
<body>
  <canvas id="canvas" width="${size}" height="${size}"></canvas>
  <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = function() {
      ctx.drawImage(img, 0, 0);
      canvas.toBlob(function(blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'icon-${size}x${size}.png';
        a.click();
      });
    };
    
    const svg = \`${createSVG(size).replace(/`/g, '\\`')}\`;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    img.src = URL.createObjectURL(blob);
  </script>
</body>
</html>
`;

console.log('\n🎨 PWA Icon Generator\n');
console.log('Creating placeholder icons for A-Cube PWA...\n');

// Generate SVG files
sizes.forEach(size => {
  const svgPath = path.join(iconsDir, `icon-${size}x${size}.svg`);
  fs.writeFileSync(svgPath, createSVG(size));
  console.log(`✓ Created: icon-${size}x${size}.svg`);
});

// Create maskable icons (with padding)
const createMaskableSVG = (size) => {
  const padding = size * 0.1;
  const innerSize = size - (padding * 2);
  return `
<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="#8B5CF6"/>
  <rect x="${padding}" y="${padding}" width="${innerSize}" height="${innerSize}" 
        fill="#6366F1" rx="${innerSize * 0.15}"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${size * 0.35}" 
        font-weight="bold" fill="white" text-anchor="middle" dy=".35em">A</text>
</svg>
`;
};

[192, 512].forEach(size => {
  const svgPath = path.join(iconsDir, `icon-maskable-${size}x${size}.svg`);
  fs.writeFileSync(svgPath, createMaskableSVG(size));
  console.log(`✓ Created: icon-maskable-${size}x${size}.svg`);
});

console.log('\n📝 Note: SVG icons created. For production, convert to PNG format.');
console.log('   Use online tools like https://realfavicongenerator.net/\n');
console.log('✅ PWA icon generation complete!\n');
