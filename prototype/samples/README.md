# Synthetic sample meal image

## Additional overhead viewpoint - 2026-11-18

`demo-meal-top-view.png` is a separate, directly overhead view of the current side-of-table meal scene, created with the built-in image-generation tool and the imagegen skill. It retains the Chinese chicken/vegetable dish, rice bowl, blue-and-white porcelain and the diner's hands, with no face visible. `demo-meal.png` and the older `demo-meal-overhead.png` remain unchanged. The default runner image is unchanged. The new PNG was copied without pixel edits and visually checked.

Final edit prompt:

> Use case: precise-object-edit. Edit target: the supplied fictional Chinese home-meal image. Generate another viewpoint of exactly this scene, now photographed from DIRECTLY ABOVE the dining table, a true overhead top-down camera looking vertically down. Preserve the same wooden tabletop, same blue-and-white Chinese porcelain plate of chicken stir-fried with broccoli and carrot slices in light sauce, matching separate rice bowl to the right, and same older diner in navy cardigan and checked shirt actively eating with wooden chopsticks. Show the entire round plate and rice bowl from above, with the food and dish contents clearly visible and natural relative sizes. Keep the diner at the top edge of the frame: only forearms, hands and a small part of clothed torso visible, one hand holding chopsticks with a piece of chicken above the plate, other hand beside the rice bowl. Do not show any face, head, eyes, mouth or identifiable portrait. Maintain soft natural window light, realistic food and wooden textures, generous tabletop surrounding the meal, landscape composition. This is a change of camera viewpoint, not a different meal: preserve dish identity, porcelain pattern, food types and setting. No text, logos, watermarks, medical devices or camera device visible. Synthetic demonstration content.


The original overhead image, preserved as `demo-meal-overhead.png`, was created on 2026-11-09 with the built-in image-generation tool, using the imagegen skill. It depicts rice, chicken, broccoli and carrots on a white plate. It is a fictional demonstration asset, not an actual patient record, calibrated portion reference or dietary recommendation.

The image is intended for the existing meal-submission JSON request. Its pixels do not determine the current fixed food/glucose estimates; CV and glucose analysis remain stubs. Starting the server does not automatically process or email the photo.

## Original generation prompt

> Use case: photorealistic-natural. Asset type: synthetic meal photograph for a university food-recording software prototype. Primary request: a realistic overhead smartphone-style photo of an ordinary home-cooked Chinese lunch on a light wooden dining table: one white ceramic plate containing steamed white rice, cooked sliced chicken, broccoli and carrot pieces. Entire plate visible, food items clearly distinguishable, natural window light, realistic portions and food textures, square composition. No people, no text, no nutrition labels, no medical devices, no logos, no watermark. This is a fictional demonstration image, not evidence of an actual patient's meal or a dietary recommendation.

Generation used an opaque background and no reference images. The selected PNG was copied into this project without changing its pixels.


## Earlier distant meal variant - 2026-11-16

The earlier `demo-meal.png` variant was the farther-away, low-angle Chinese home-meal variant, generated with the built-in image-generation tool using the imagegen skill. It shows a shared chicken, broccoli and carrot stir-fry on blue-and-white porcelain, a separate rice bowl and chopsticks, with surrounding wooden tabletop visible. It remains fictional and does not alter the fixed nutritional/glucose estimates. The previous overhead asset is preserved. An intermediate low-angle close view remains in the generator output directory, rather than adding another project asset.

The final edit used the intermediate low-angle image as its reference. Final prompt:

> Use case: precise-object-edit. Edit the supplied meal photograph for a fictional university food-monitoring prototype. Keep the low oblique table-level camera angle, but move the camera substantially farther away, about 1 to 1.5 metres from the food: a medium-wide environmental photo, with the entire main plate occupying only about 40 to 45 percent of image width, ample wooden tabletop visible in front and around it. Make the meal unmistakably a Chinese home-cooked dish: a shared blue-and-white Chinese porcelain plate holding glossy wok-stir-fried chicken pieces mixed together with broccoli and carrot slices in a light soy-based sauce; steamed white rice served separately in a small Chinese porcelain rice bowl beside the plate, with a pair of wooden chopsticks resting alongside. This is a simple everyday Chinese family meal rather than a Western composed plate or restaurant presentation. Soft natural window lighting, realistic casual smartphone photo, landscape composition, low perspective approximately 15 degrees above the table. No people, text, watermarks, logos or medical devices. Do not make a close-up; show the whole table setting with generous surrounding space.

The generated PNG was copied without pixel modifications into the existing default image path. Preview without sending: `python prototype/run_demo.py --html-preview prototype/output/caregiver-chinese-meal.html`.


## Current default: side-of-table camera with diner - 2026-11-16

The current `demo-meal.png` shows a low side-of-table camera view with a person eating. Their hands and torso are visible; their face is outside the frame. The wooden table edge, full stir-fry plate and rice bowl are visible. This synthetic image supersedes the empty-table variant above. The built-in image-generation tool edited that earlier Chinese meal image. No real patient is depicted.

Final edit prompt:

> Use case: precise-object-edit. Edit the referenced fictional Chinese meal photo into a realistic camera capture from a companion device positioned at the SIDE EDGE of the dining table looking diagonally across the tabletop while a person is eating. Camera lens is about 20 cm above tabletop, low oblique viewpoint, medium-wide landscape frame from roughly 1 metre away. Show the near side edge of the wooden table in the foreground and the tabletop, all dishes and the food clearly. An older adult is seated on the far side of the table actively eating with chopsticks, one hand using chopsticks to pick up a piece of food and the other resting near a rice bowl. ONLY their clothed torso, forearms and hands are in frame. Crop the entire head and neck out above the shoulders: absolutely no face, eyes, mouth, chin or head, including reflections. Keep the everyday Chinese home meal: shared blue-and-white porcelain plate of chicken stir-fried with broccoli and carrot slices in light sauce, and a separate bowl of steamed white rice. Include the full plate, bowl and their food in frame; hands must not obscure the main dish. The food occupies the central tabletop, person beyond the dishes, natural candid domestic setting with soft daylight. Ordinary monitoring-camera style, not a staged commercial food close-up and not an overhead shot. No camera device or pet visible, no text, watermark or medical devices. All people and food are synthetic demonstration content.

The asset was copied without pixel modifications. Local preview: `python prototype/run_demo.py --html-preview prototype/output/caregiver-table-side.html`.
