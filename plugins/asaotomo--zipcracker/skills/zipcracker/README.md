### Tool Introduction

------

***ZipCracker is a high-performance, multi-threaded cracking suite developed by Team Hx0. Designed specifically for penetrating password-protected ZIP archives, it utilizes a "Cost-Ascending Tactical Pipeline" including zero-interaction CRC32 collisions, dynamic dictionary attacks, and advanced mask attacks. It can also identify and automatically repair "pseudo-encrypted" archives, making it the ultimate weapon for CTF competitions and red team operations.***

🚀 **The Ultimate OpenClaw AI Agent Skill (V3.0.0)** ZipCracker is now natively integrated with the OpenClaw ecosystem. It is no longer just a CLI script; it is an **Autonomous Agent Tool**. You can deploy it as a Skill and crack ZIP files purely through natural language. If standard attacks fail, the Agent will ask you for OSINT (Open Source Intelligence) clues to dynamically write Python scripts, generate highly targeted custom dictionaries on the fly, and execute surgical strikes against the target!

<img width="1510" alt="image" src="https://github.com/user-attachments/assets/c698572c-2ea5-4f22-820d-5cf512eb70ec" />

**Key Features & Updates:**

1. **Zero-Interaction CRC32 Collision:** The program automatically checks file sizes within encrypted archives. For any file smaller than 6 bytes, it will bypass all manual prompts and instantly execute a CRC32 hash collision attack, recovering the plaintext in milliseconds.
2. **Massive Dictionary Support:** Comes with over 6,000 common passwords and automatically generates 1-6 digit numeric combinations. It efficiently handles custom dictionaries, even massive ones containing hundreds of millions of entries.
3. **Dynamic Threading:** Automatically adjusts the optimal number of threads based on your CPU architecture and runtime environment, ensuring the cracking process is blazingly fast and stable.
4. **AES Decryption Support:** Fully supports traditional ZipCrypto as well as modern AES-encrypted archives. 
5. **Agent-Native Auto-Healing:** If an AES-encrypted file is detected but the required `pyzipper` library is missing, the tool will automatically invoke `pip` in the background to install the dependency and seamlessly resume the attack without crashing the Agent's context.

### Usage

------

#### 1. Pseudo-Encryption Identification and Repair

Detects pseudo-encryption flag bits and automatically repairs the archive, generating a clean, unencrypted output directory.

```bash
python3 ZipCracker.py test01.zip  

```

#### 2. Brute Force Cracking - Built-in Dictionary

Automatically chains through the built-in dictionary and the auto-generated 1-6 digit numeric lists.

```bash
python3 ZipCracker.py test02.zip  

```

#### 3. Brute Force Cracking - Custom Dictionary

We provide two ways to load custom dictionaries:

1. **Single File:** Specify your custom dictionary directly:

```bash
python3 ZipCracker.py test02.zip YourDict.txt

```

2. **Directory Mode:** Point the script to a directory containing multiple dictionary files. It will sequentially load and test each dictionary until the password is found:

```bash
python3 ZipCracker.py test02.zip YourDictDirectory

```

#### 4. Brute Force Cracking - CRC32 Collision

No manual intervention required. If small files (<= 6 bytes) are detected, it will automatically crack them and print the internal content.

```bash
python3 ZipCracker.py test03.zip  

```

#### 5. Brute Force Cracking - Mask Attack (The Sniper Strike)

When you know the partial structure of the password (e.g., company name + year), a mask attack is the most efficient method. Use special placeholders to define the password's format, significantly narrowing the search space.

**Mask Placeholder Rules:**

| Placeholder | Character Set Represented |
| --- | --- |
| `?d` | Digits (0-9) |
| `?l` | Lowercase Letters (a-z) |
| `?u` | Uppercase Letters (A-Z) |
| `?s` | Special Symbols (!@#$etc.) |
| `??` | The `?` character itself |

```bash
python3 ZipCracker.py test04.zip -m '?uali?s?d?d?d'

```

*The command above will attempt to crack a password structured as: an uppercase letter + 'ali' + a special symbol + three digits (e.g., Kali@123, Bali#756).*

#### 6. AI Agent Mode (Quiet Mode)

When integrating with AI Agents (like OpenClaw) or running in automated CI/CD pipelines, append the `-q` or `--quiet` flag. This strips out all `\r` real-time progress bars, suppresses all terminal noise, and forces auto-execution of dependencies and collisions. It outputs strictly the final result, preventing LLM token overflow and context degradation.

```bash
python3 ZipCracker.py test04.zip -q

```

---

**Disclaimer:** This tool is provided for security researchers and penetration testers for self-assessment and educational purposes only. The author and Hx0 Team are not responsible for any misuse or consequences caused by users. Users must comply with local laws. This program should not be used for illegal or commercial purposes.

---

**【Support with Tips ❤️】 Code Connects Hearts Across Mountains and Seas, Every Bit of Support Warms Like Sunshine ✨**

While our code is fully open-source, every cup of coffee fuels our journey to go further and build better tools ☕️

**【Team Official Account】Scan and follow the Hx0 Team official account for the latest updates and security research.**

**【Team Knowledge Planet】Big Giveaway inside!**