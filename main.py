import os
import heapq
import json
import time
import matplotlib.pyplot as plt

# --- Node Class for Huffman Tree ---
class HeapNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        if other is None or not isinstance(other, HeapNode):
            return False
        return self.freq == other.freq

# --- Main Huffman Coding Class ---
class HuffmanCoding:
    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    def make_frequency_dict(self, text):
        frequency = {}
        for character in text:
            frequency[character] = frequency.get(character, 0) + 1
        return frequency

    def make_heap(self, frequency):
        for key, value in frequency.items():
            heapq.heappush(self.heap, HeapNode(key, value))

    def merge_nodes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, root, current_code):
        if root is None:
            return
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        self.make_codes_helper(root, "")

    def get_encoded_text(self, text):
        return "".join([self.codes[char] for char in text])

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - (len(encoded_text) % 8)
        encoded_text += "0" * extra_padding
        padded_info = "{0:08b}".format(extra_padding)
        return padded_info + encoded_text

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            raise ValueError("Encoded text not padded properly")
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            b.append(int(padded_encoded_text[i:i+8], 2))
        return b

    def compress(self):
        filename, _ = os.path.splitext(os.path.basename(self.path))
        output_path = os.path.join("compressed_files", filename + ".bin")
        meta_path = os.path.join("compressed_files", filename + "_meta.json")

        with open(self.path, 'r', encoding='utf-8') as file:
            text = file.read().rstrip()

        frequency = self.make_frequency_dict(text)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()

        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        byte_array = self.get_byte_array(padded_encoded_text)

        with open(output_path, 'wb') as output:
            output.write(bytes(byte_array))

        with open(meta_path, 'w', encoding='utf-8') as meta_file:
            json.dump(self.reverse_mapping, meta_file)

        return output_path, meta_path

    def remove_padding(self, padded_encoded_text):
        extra_padding = int(padded_encoded_text[:8], 2)
        return padded_encoded_text[8: -extra_padding if extra_padding != 0 else None]

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = []
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text.append(self.reverse_mapping[current_code])
                current_code = ""
        return "".join(decoded_text)

    def decompress(self, input_path, meta_path):
        filename, _ = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join("decompressed_files", filename + "_decompressed.txt")

        with open(meta_path, 'r', encoding='utf-8') as meta_file:
            self.reverse_mapping = json.load(meta_file)

        with open(input_path, 'rb') as file:
            bit_string = "".join(f"{byte:08b}" for byte in file.read())

        encoded_text = self.remove_padding(bit_string)
        decompressed_text = self.decode_text(encoded_text)

        with open(output_path, 'w', encoding='utf-8') as output:
            output.write(decompressed_text)

        return output_path

# --- Utility Functions ---
def setup_github_structure():
    folders = ['input_files', 'compressed_files', 'decompressed_files', 'outputs', 'images']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create a basic .gitignore
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write("__pycache__/\n*.bin\n*.json\n*.txt\n!input_files/sample.txt\n")

def generate_dashboard_image(orig_size, comp_size, ratio):
    labels = ['Original Size', 'Compressed Size']
    sizes = [orig_size, comp_size]
    colors = ['#ff9999', '#66b3ff']

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, sizes, color=colors, width=0.5)

    plt.title('File Compression Analysis Dashboard', fontsize=14, fontweight='bold')
    plt.ylabel('Size in Bytes', fontsize=12)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (orig_size*0.01), f'{yval} Bytes', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.text(0.5, max(sizes)*0.85, f'Space Saved: {100 - ratio:.2f}%', fontsize=12, ha='center', bbox=dict(facecolor='#ffff99', alpha=0.8, edgecolor='black'))

    img_path = os.path.join("images", "compression_dashboard.png")
    plt.savefig(img_path)
    plt.close()
    return img_path

def generate_report(orig_size, comp_size, ratio, output_dir="outputs"):
    report_path = os.path.join(output_dir, "compression_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== DYNAMIC FILE COMPRESSION REPORT ===\n")
        f.write(f"Date & Time: {time.ctime()}\n")
        f.write(f"Original File Size   : {orig_size} bytes\n")
        f.write(f"Compressed File Size : {comp_size} bytes\n")
        f.write(f"Total Space Saved    : {ratio:.2f}%\n")
        f.write("Status: SUCCESS\n")
    return report_path

# --- Main CLI Execution ---
if __name__ == "__main__":
    setup_github_structure()
    print("\n" + "="*50)
    print("🚀 DYNAMIC FILE COMPRESSION UTILITY 🚀")
    print("="*50)

    # Generate a professional sample log file
    sample_path = os.path.join("input_files", "sample.txt")
    if not os.path.exists(sample_path):
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write("=== SYSTEM ACTIVITY LOGS ===\n")
            f.write("Generated by: Dynamic File Compression Utility\n")
            f.write("="*40 + "\n\n")
            for i in range(1, 201):
                f.write(f"[2026-06-02 10:15:{i%60:02d}] INFO: System initialized successfully. Module {i} loaded.\n")
                f.write(f"[2026-06-02 10:15:{i%60:02d}] DEBUG: Checking data integrity for block {i * 1024}...\n")
                if i % 10 == 0:
                    f.write(f"[2026-06-02 10:16:{i%60:02d}] WARNING: High CPU usage detected in Node {i}.\n")
                if i % 25 == 0:
                    f.write(f"[2026-06-02 10:17:{i%60:02d}] ERROR: Connection timeout for API endpoint /data/{i}.\n")
            f.write("\n=== END OF LOGS ===\n")
    
    print("\n📂 Project structure generated successfully.")
    
    user_input = input("Enter file path to compress (Press ENTER for default 'input_files/sample.txt'): ").strip()
    target_file = user_input if user_input else sample_path

    if not os.path.exists(target_file):
        print(f"❌ Error: File '{target_file}' not found.")
    else:
        try:
            huffman = HuffmanCoding(target_file)
            
            print("\n⏳ Compressing file...")
            start_time = time.time()
            compressed_file, meta_file = huffman.compress()
            print(f"✅ Compression successful in {time.time() - start_time:.4f} seconds!")

            # Calculate and display stats
            orig_size = os.path.getsize(target_file)
            comp_size = os.path.getsize(compressed_file)
            savings = 100 - ((comp_size / orig_size) * 100) if orig_size > 0 else 0
            
            print("\n📊 --- COMPRESSION STATS ---")
            print(f"Original Size : {orig_size} bytes")
            print(f"Compressed    : {comp_size} bytes")
            print(f"Space Saved   : {savings:.2f}%")
            
            # Generate Report and Dashboard
            report_file = generate_report(orig_size, comp_size, savings)
            img_path = generate_dashboard_image(orig_size, comp_size, (comp_size / orig_size) * 100)
            
            print(f"📄 Text Report saved to: {report_file}")
            print(f"🖼️ Dashboard Image saved to: {img_path}")

            # Decompression prompt
            choice = input("\n🔄 Do you want to decompress and verify? (y/n): ").strip().lower()
            if choice == 'y':
                print("⏳ Decompressing...")
                decomp_start = time.time()
                output_path = huffman.decompress(compressed_file, meta_file)
                print(f"✅ Decompressed successfully in {time.time() - decomp_start:.4f} seconds!")
                print(f"📁 Original file restored at: {output_path}")
        except Exception as e:
            print(f"❌ An error occurred: {e}")