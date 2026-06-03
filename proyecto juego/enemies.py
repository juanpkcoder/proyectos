# enemies.py — Definiciones de enemigos y sus propiedades
from settings import *


class EnemyData:
    """Datos de un tipo de enemigo."""

    def __init__(self, name, hp, atk, defense, exp_reward, gold_reward,
                 intro_text, flavor_texts, act_options, act_texts,
                 mercy_needed, sprite_color, attack_patterns):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.intro_text = intro_text
        self.flavor_texts = flavor_texts
        self.act_options = act_options
        self.act_texts = act_texts
        self.mercy_needed = mercy_needed
        self.sprite_color = sprite_color
        self.attack_patterns = attack_patterns
        self.mercy_count = 0
        self.spareable = False

    def reset(self):
        self.hp = self.max_hp
        self.mercy_count = 0
        self.spareable = False

    def check_mercy(self):
        if self.mercy_count >= self.mercy_needed:
            self.spareable = True
        return self.spareable

    def get_flavor(self):
        import random
        return random.choice(self.flavor_texts)


def create_florin():
    """Florín — Una flor amigable (tutorial)."""
    return EnemyData(
        name="Florín",
        hp=18, atk=4, defense=1,
        exp_reward=10, gold_reward=5,
        intro_text="* ¡Florín aparece saltando alegremente!",
        flavor_texts=[
            "* Florín te mira con curiosidad.",
            "* Florín baila moviendo sus pétalos.",
            "* Florín tararea una melodía.",
            "* Huele a primavera.",
        ],
        act_options=["Hablar", "Acariciar", "Oler"],
        act_texts={
            "Hablar": "* Le dices a Florín que es muy bonita.\n* ¡Florín se sonroja!",
            "Acariciar": "* Acaricias los pétalos de Florín.\n* Florín está encantada.",
            "Oler": "* Hueles a Florín.\n* ¡Un aroma maravilloso!",
        },
        mercy_needed=2,
        sprite_color=(80, 220, 80),
        attack_patterns=["petal_drift", "seed_rain"],
    )


def create_huesitos():
    """Huesitos — Un esqueleto bromista."""
    return EnemyData(
        name="Huesitos",
        hp=30, atk=6, defense=3,
        exp_reward=25, gold_reward=12,
        intro_text="* ¡Huesitos bloquea tu camino con una sonrisa!",
        flavor_texts=[
            "* Huesitos te cuenta un chiste malo.",
            "* Huesitos hace sonar sus huesos rítmicamente.",
            "* Huesitos está esperando que te rías.",
            "* Huele a ketchup.",
        ],
        act_options=["Chiste", "Bailar", "Reír"],
        act_texts={
            "Chiste": "* Le cuentas un chiste a Huesitos.\n* ¡Se ríe tanto que se desarma!",
            "Bailar": "* Bailas con Huesitos.\n* Sus movimientos son... esqueléticos.",
            "Reír": "* Te ríes de su último chiste.\n* Huesitos parece muy contento.",
        },
        mercy_needed=3,
        sprite_color=(230, 230, 230),
        attack_patterns=["bone_horizontal", "bone_vertical"],
    )


def create_sombra():
    """Sombra — Un fantasma misterioso (boss)."""
    return EnemyData(
        name="Sombra",
        hp=50, atk=8, defense=4,
        exp_reward=50, gold_reward=30,
        intro_text="* La oscuridad se concentra...\n* ¡Sombra emerge de las tinieblas!",
        flavor_texts=[
            "* Sombra flota silenciosamente.",
            "* Los ojos de Sombra brillan en la oscuridad.",
            "* Sombra parece... triste.",
            "* Una brisa fría te rodea.",
        ],
        act_options=["Consolar", "Cantar", "Iluminar"],
        act_texts={
            "Consolar": "* Le dices a Sombra que no está sola.\n* Sombra tiembla ligeramente...",
            "Cantar": "* Cantas una canción suave.\n* Sombra parece calmarse un poco.",
            "Iluminar": "* Sacas una pequeña luz.\n* La oscuridad retrocede... Sombra duda.",
        },
        mercy_needed=4,
        sprite_color=(120, 60, 180),
        attack_patterns=["ghost_orbs", "shadow_wave", "ghost_orbs"],
    )
