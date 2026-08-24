import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "Qwen/Qwen2.5-0.5B-Instruct"

print(f"--- Chargement du modèle {model_id} ---")
tokenizer = AutoTokenizer.from_pretrained(model_id)

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

print(f"Utilisation du périphérique : {device} ({dtype})")

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=dtype,
    device_map="auto"
)
print("Modèle chargé avec succès !\n")

def tester_requete(prompt: str, max_new_tokens: int = 150):
    messages = [
        {"role": "system", "content": "Tu es un assistant IA concis et utile."},
        {"role": "user", "content": prompt}
    ]
    
    # 1. Application du template de chat
    formatted_prompt = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # Encodage en tokens
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)
    prompt_tokens = inputs["input_ids"].shape[1]
    
    # 2. Génération avec mesure du temps
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    elapsed_time = time.time() - start_time
    
    # 3. Calcul et statistiques des tokens
    total_tokens = outputs.shape[1]
    completion_tokens = total_tokens - prompt_tokens
    tokens_per_sec = completion_tokens / elapsed_time if elapsed_time > 0 else 0
    
    # Décodage du texte généré (sans les tokens du prompt)
    generated_text = tokenizer.decode(outputs[0][prompt_tokens:], skip_special_tokens=True)
    
    print("=" * 60)
    print(f"📥 REQUÊTE : {prompt}")
    print("-" * 60)
    print(f"📤 RÉPONSE :\n{generated_text.strip()}")
    print("-" * 60)
    print("📊 STATISTIQUES DES TOKENS :")
    print(f" • Tokens du Prompt (Entrée)   : {prompt_tokens}")
    print(f" • Tokens Générés (Sortie)     : {completion_tokens}")
    print(f" • Total Tokens Consommés      : {total_tokens}")
    print(f" • Temps de calcul             : {elapsed_time:.2f} s ({tokens_per_sec:.1f} tokens/s)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    # Tests d'exemples automatiques
    tester_requete("Explique la gravité en une phrase simple.")
    tester_requete("Donne-moi 3 idées de projets en Python pour débutant.")
    
    # Mode interactif pour tester vos propres requêtes
    print("Vous pouvez maintenant tester vos propres requêtes en direct (tapez 'exit' pour quitter) :\n")
    while True:
        try:
            user_input = input("Votre question > ")
            if not user_input.strip() or user_input.lower() in ["exit", "quit", "q"]:
                print("Fin des tests.")
                break
            tester_requete(user_input)
        except KeyboardInterrupt:
            print("\nArrêt.")
            break
