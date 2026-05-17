import { writeFile } from "fs/promises";

const FAL_API_KEY = process.env.FAL_API_KEY;
if (!FAL_API_KEY) {
  console.error("FAL_API_KEY required. Run with: FAL_API_KEY=... node scripts/generate-comparison.mjs");
  process.exit(1);
}

async function generateImage(prompt, name) {
  console.log(`\nGenerating: ${name}`);
  console.log(`Prompt: ${prompt.slice(0, 80)}...`);

  const response = await fetch("https://fal.run/fal-ai/z-image/turbo", {
    method: "POST",
    headers: {
      Authorization: `Key ${FAL_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      image_size: "square_hd",
      num_images: 1,
      num_inference_steps: 8,
      enable_safety_checker: true,
      output_format: "webp",
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`fal.ai failed (${response.status}): ${text}`);
  }

  const data = await response.json();
  const imageUrl = data.images[0].url;
  console.log(`Image URL: ${imageUrl}`);

  const imgResponse = await fetch(imageUrl);
  const buffer = Buffer.from(await imgResponse.arrayBuffer());
  const outPath = `comparison-${name}.webp`;
  await writeFile(outPath, buffer);
  console.log(`Saved: ${outPath} (${(buffer.length / 1024).toFixed(1)} KB)`);

  return outPath;
}

// Verse 1-8: 中夜狗吠，盜在墻外。神明祐助，銷散皆去。
// "In the middle of the night the dog barks; thieves lurk beyond the wall.
//  By the spirits' aid and protection, all scatter and depart."

// Approach 1: Direct — raw Chinese text + style suffix
const directPrompt =
  "中夜狗吠，盜在墻外。神明祐助，銷散皆去。Chinese ink painting style.";

// Approach 2: One-shot — what a generic LLM produces without the skill
const oneshotPrompt =
  "A nighttime scene of divine protection. A dog guards a traditional Chinese courtyard under moonlight. Peaceful atmosphere with a sense of spiritual safety. Thieves flee in the distance. Mountains and clouds beyond. Chinese ink painting style.";

await generateImage(directPrompt, "direct");
await generateImage(oneshotPrompt, "oneshot");

console.log("\nDone! Now update the slide image paths.");
