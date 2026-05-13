export const allTools = ["run_coder_agent", "run_git_agent", "run_docs_agent"];

export async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
}
export function stringToColor(str: string): string {
  // Generate hash from string
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Convert to HSL for theme-appropriate colors
  const h = Math.abs(hash) % 360; // Hue: 0-360
  const s = 50 + (Math.abs(hash >> 8) % 30); // Saturation: 50-80%
  const l = 25 + (Math.abs(hash >> 16) % 20); // Lightness: 25-45% for dark backgrounds

  // Add secondary hue rotation for more variation
  const h2 = (h + 137) % 360; // Golden angle rotation
  const finalHue = hash % 2 === 0 ? h : h2;

  return `hsl(${finalHue}, ${s}%, ${l}%)`;
}

// Get contrasting text color for a background
export function getContrastTextColor(backgroundColor: string): string {
  // Extract HSL values from the background color
  const hslMatch = backgroundColor.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
  if (!hslMatch) return '#e0e6eb'; // Default light text
  
  const lightness = parseInt(hslMatch[3]);
  
  // If background is dark (lightness < 50%), use light text
  // If background is light (lightness >= 50%), use dark text
  return lightness < 50 ? '#e0e6eb' : '#0a0f1b';
}