import gradio as gr
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer, util

class StyleTransfer:
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )

        self.style_bert = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    def generate_style_transfer(self, input_text, style_examples, temperature=0.7, max_new_tokens=150):
        style_examples = [ex.strip() for ex in style_examples.split("\n") if ex.strip()]

        style_prompt = "\n".join([f"Example {i+1}: {ex}" for i, ex in enumerate(style_examples)])

        messages = [
            {"role": "user", "content": f"""Rewrite the following text in the same style as these examples:
            {style_prompt}

            Text to rewrite: {input_text}

            Output ONLY the rewritten text without any additional explanation or formatting."""}
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("[/INST]")[-1].strip()

    def calculate_style_similarity(self, transformed_text, style_examples):
        style_examples = [ex.strip() for ex in style_examples.split("\n") if ex.strip()]
        embeddings = self.style_bert.encode(
            [transformed_text] + style_examples,
            convert_to_tensor=True
        )
        cos_sim = util.cos_sim(embeddings[0], embeddings[1:])
        return torch.mean(cos_sim).item()


styler = StyleTransfer()

def run_style_transfer(input_text, style_examples, temperature, max_tokens):
    transformed = styler.generate_style_transfer(
        input_text,
        style_examples,
        temperature=temperature,
        max_new_tokens=max_tokens
    )

    similarity = styler.calculate_style_similarity(transformed, style_examples)

    return transformed, round(similarity, 2)

preset_styles.update({
    "Jane Austen (Romantic)": "\n".join([
        "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
        "My good opinion once lost, is lost forever.",
        "There is no charm equal to tenderness of heart."
    ]),
    "J.K. Rowling (Magical)": "\n".join([
        "The castle loomed in the distance, its turrets piercing the misty Scottish sky.",
        "It does not do to dwell on dreams and forget to live.",
        "The scar had not pained Harry for nineteen years. All was well."
    ]),
    "H.P. Lovecraft (Cosmic Horror)": "\n".join([
        "The oldest and strongest emotion of mankind is fear, and the oldest and strongest kind of fear is fear of the unknown.",
        "That is not dead which can eternal lie, And with strange aeons even death may die.",
        "The night was dank and breathless, the air tinged with miasmal vapors."
    ]),

    "Elon Musk Tweet": "\n".join([
        "🚀 Exciting progress on Starship! Mars colonization looking increasingly feasible!",
        "The future of AI must be decentralized. Neuralink prototype trials show promising results.",
        "To those who doubt: Watch this ⚡"
    ]),
    "Gen-Z TikTok": "\n".join([
        "No cap, this bussin' frfr 🥵👌",
        "Sksksk I can't even rn 💀",
        "Spill the tea bestie ☕👀"
    ]),
    "David Attenborough (Nature Doc)": "\n".join([
        "Here, in the dense Amazonian jungle, life thrives in its most primal form.",
        "The leopard seal moves with lethal grace through the icy waters.",
        "Nature's great drama unfolds before our very eyes."
    ]),

    "Cyberpunk Dialogue": "\n".join([
        "The neon reflected in her ocular implants as she jacked into the datastream.",
        "You wanna hack the megacorp? That's a one-way ticket to brainfry, choomba.",
        "The synthwave hummed through the rain-soaked streets of Neo-Tokyo."
    ]),
    "Romance Novel": "\n".join([
        "His smoldering gaze locked with hers across the crowded ballroom.",
        "The electricity between them could power a small city.",
        "She knew she should resist, but her heart had other plans."
    ]),
    "Hard Sci-Fi": "\n".join([
        "The quantum drive hummed at 0.8 past lightspeed, warping spacetime itself.",
        "Calculations showed a 73.6% chance the alien artifact predated the Big Bang.",
        "Her neural lace recorded every femtosecond of the singularity event."
    ]),

    "Yoda Wisdom": "\n".join([
        "Do or do not. There is no try.",
        "Fear is the path to the dark side.",
        "When nine hundred years old you reach, look as good you will not."
    ]),
    "Detective Noir": "\n".join([
        "The dame walked into my office like trouble wearing stockings.",
        "It was rainin' like a broad with a broken umbrella in this burg.",
        "The .38 felt cold in my hand, colder than my ex's heart."
    ]),
    "Haiku Mode": "\n".join([
        "Cherry blossoms fall / Soft whispers of spring's farewell / Moon watches in silence",
        "Winter's icy grip / Broken by the sparrow's song / Hope takes flight again"
    ]),

    "Resume Bullet Points": "\n".join([
        "Spearheaded cross-functional team to deliver 40% YOY growth in key metrics",
        "Optimized CI/CD pipelines reducing deployment times by 65%",
        "Pioneered blockchain-based solution securing $2.5M in seed funding"
    ]),
    "Customer Service Reply": "\n".join([
        "Thank you for reaching out! I'd be happy to help resolve this issue.",
        "We sincerely apologize for the inconvenience you've experienced.",
        "Please allow 24-48 hours for our team to investigate this matter."
    ]),
    "Academic Paper": "\n".join([
        "The results demonstrate a statistically significant correlation (p < 0.05).",
        "This study builds upon prior work by Smith et al. (2020) while addressing key limitations.",
        "Methodology followed a double-blind protocol with placebo control group."
    ])
})

style_choice = gr.Dropdown(
    choices=[
        ("🎭 Literary Masters", "Shakespeare"),
        ("🎭 Literary Masters", "Jane Austen (Romantic)"),
        ("🎭 Literary Masters", "J.K. Rowling (Magical)"),
        ("🎭 Literary Masters", "H.P. Lovecraft (Cosmic Horror)"),
        ("🤖 Modern Culture", "Elon Musk Tweet"),
        ("🤖 Modern Culture", "Gen-Z TikTok"),
        ("🤖 Modern Culture", "Gordon Ramsay Roast"),
        ("📚 Genre Fiction", "Cyberpunk Dialogue"),
        ("📚 Genre Fiction", "Romance Novel"),
        ("📚 Genre Fiction", "Hard Sci-Fi"),
        ("📚 Genre Fiction", "Detective Noir"),
        ("💼 Professional", "Tech Blog"),
        ("💼 Professional", "Legal Document"),
        ("💼 Professional", "Resume Bullet Points"),
        ("💼 Professional", "Academic Paper"),
        ("😂 Fun Styles", "Pirate Speak"),
        ("😂 Fun Styles", "Marketing Buzzwords"),
        ("😂 Fun Styles", "Yoda Wisdom"),
        ("😂 Fun Styles", "Haiku Mode"),
        ("🌍 Miscellaneous", "David Attenborough (Nature Doc)"),
        ("🌍 Miscellaneous", "Customer Service Reply"),
        ("🌍 Miscellaneous", "Reddit Casual")
    ],
    label="Preset Styles",
    value="Shakespeare",
    allow_custom_value=True
)

with gr.Blocks(title="StyleMimic", theme=gr.themes.Default(primary_hue="purple")) as demo:
    gr.Markdown("""
    # 🎨 StyleMimic
    *Transform text into any style imaginable!*
    """)

def update_style_examples(style_choice):
    return preset_styles[style_choice]

with gr.Blocks(title="EchoForge") as demo:
    gr.Markdown("# 🎭 EchoForge - Cast Your Words in Borrowed Voices")

    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(label="Input Text", lines=3,
                                  placeholder="Enter text to transform...")
            style_choice = gr.Dropdown(
                choices=list(preset_styles.keys()),
                label="Preset Styles",
                value="Shakespeare"
            )
            style_examples = gr.Textbox(label="Style Examples (one per line)", lines=4,
                                       placeholder="Enter 2-3 style examples...")
            temperature = gr.Slider(0.1, 1.0, value=0.7, label="Creativity (Temperature)")
            max_tokens = gr.Slider(50, 300, value=150, step=10, label="Max Output Length")
            submit_btn = gr.Button("Transform Style!", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(label="Transformed Text", interactive=False)
            similarity_score = gr.Number(label="Style Similarity Score", precision=2)

    style_choice.change(
        fn=update_style_examples,
        inputs=style_choice,
        outputs=style_examples
    )

    submit_btn.click(
        fn=run_style_transfer,
        inputs=[input_text, style_examples, temperature, max_tokens],
        outputs=[output_text, similarity_score]
    )

if __name__ == "__main__":
    demo.launch(share=False)