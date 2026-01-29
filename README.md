# Department Display Board - Proof of Concept

A professional slideshow display board system using pure HTML/CSS/JavaScript, designed to run on the department iMac display.

## Features

- **Auto-rotating slides** - 7 seconds per slide with smooth fade transitions
- **Mixed content** - 13 images + informational text slides
- **Real-time clock** - Live date and time display in footer
- **Progress indicator** - Visual progress bar showing slide timing
- **Keyboard controls** - Arrow keys to navigate, 'F' for fullscreen
- **Responsive design** - Adapts to any display size
- **Professional styling** - Blue gradient theme with high contrast text
- **Zero dependencies** - No frameworks, no npm, no build process

## Quick Start

### On the iMac

1. **Open the slideshow:**
   ```bash
   cd ~/department-display
   open index.html
   ```
   Or simply double-click `index.html`

2. **Enter fullscreen mode:**
   - Press `F11` (browsers)
   - Press `Cmd+Shift+F` (Safari)
   - Or press `F` key after page loads

3. **Let it run** - The slideshow will automatically rotate through all slides

## Content

The display includes:
- Welcome slide
- Department announcements
- Upcoming events
- Student resources
- Contact information
- Recent achievements
- Important dates
- 13 custom images from originals directory

## Customization

### Change slide duration
Edit `index.html`, line 274:
```javascript
const SLIDE_DURATION = 7000; // milliseconds
```

### Add new text slides
Copy an existing text slide div and modify:
```html
<div class="slide text-slide">
    <h2>Your Title</h2>
    <ul>
        <li>Point 1</li>
        <li>Point 2</li>
    </ul>
</div>
```

### Add new images
1. Place image in `images/` folder
2. Add slide div:
```html
<div class="slide image-slide" style="background-image: url('images/your-image.jpg');"></div>
```

### Change colors
Edit the CSS gradient in `<style>` section:
```css
background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
```

## Keyboard Controls

- **Arrow Right/Left**: Manual slide navigation
- **F**: Toggle fullscreen
- **F11**: Browser fullscreen (alternative)
- **Esc**: Exit fullscreen

## GitHub Pages Deployment (Optional)

To host this on GitHub Pages:

```bash
cd ~/department-display

# Initialize git repository
git init
git add .
git commit -m "Initial department display board"

# Create GitHub repo and push
gh repo create department-display --public --source=. --remote=origin --push

# Enable GitHub Pages
gh repo edit --enable-pages --pages-branch main

# Get URL
gh repo view --web
```

Access from anywhere: `https://yourusername.github.io/department-display`

## Technical Details

**Stack:**
- Pure HTML5
- CSS3 with animations
- Vanilla JavaScript (ES6+)
- No external dependencies

**Browser Compatibility:**
- Chrome/Chromium ✓
- Firefox ✓
- Safari ✓
- Edge ✓

**Display Resolution:**
- Optimized for 1920x1080 (Full HD)
- Also works with 2560x1440 (QHD)
- Responsive to any display size

## File Structure

```
department-display/
├── index.html          # Main slideshow file
├── README.md           # This file
└── images/             # Image directory
    ├── original.jpg
    ├── original1.jpg
    ├── original2.webp
    ├── original3.jpg
    ├── original4.jpg
    ├── original5.jpg
    ├── original6.jpg
    ├── original7.jpg
    ├── original8.jpg
    ├── original9.jpg
    ├── original10.jpg
    ├── original11.jpg
    └── original12.jpg
```

## Troubleshooting

**Slides not auto-rotating:**
- Ensure JavaScript is enabled
- Check browser console for errors (F12)

**Images not showing:**
- Verify images are in `images/` folder
- Check image file names match in HTML

**Fullscreen not working:**
- Try different method: F11, Cmd+Shift+F, or press 'F'
- Some browsers require user interaction first

**Footer overlapping content:**
- Adjust slide padding in CSS if needed
- Footer height can be adjusted in `.footer` style

## Future Enhancements

Ideas for department chair to consider:

- **Google Calendar integration** - Pull events automatically
- **RSS feed** - Show department news
- **Weather widget** - Local weather display
- **Countdown timers** - For upcoming deadlines
- **Department logo** - Add branding
- **Social media feed** - Twitter/X integration
- **Emergency alerts** - Highlight urgent messages
- **Multi-language support** - For international students
- **Mobile admin panel** - Update content from phone
- **Analytics** - Track what slides get most attention

## Notes

- This is a proof of concept to demonstrate the display board idea
- All content is placeholder - customize for your department
- No server required - runs entirely in browser
- Can be hosted on GitHub Pages for easy updates
- Total cost: $0 (using free GitHub Pages)

## Contact

For questions or suggestions about this display board system, contact the department chair or technical support.

---

*Created as a proof of concept demonstration - January 2026*
