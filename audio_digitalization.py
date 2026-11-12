import argparse
from pathlib import Path
import subprocess
import tempfile

import imageio_ffmpeg
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


def load_audio(filename):
    """Load WAV, or decode MP3 to a temporary WAV first."""
    path = Path(filename)
    if path.suffix.lower() == ".wav":
        audio, rate = sf.read(path, always_2d=True)
    elif path.suffix.lower() == ".mp3":
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder) / "temporary.wav"
            subprocess.run(
                [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                 "-i", str(path), str(wav)], check=True
            )
            audio, rate = sf.read(wav, always_2d=True)
    else:
        raise ValueError("Choose an MP3 or WAV file.")
    return np.clip(audio.mean(axis=1), -1, 1), rate


def quantize(audio, bits):
    """Return signed PCM integer codes and reconstructed amplitudes."""
    if bits < 1 or bits > 24:
        raise ValueError("Choose 1–24 bits for this numerical implementation.")
    scale = 2 ** (bits - 1)
    codes = np.clip(np.rint(audio * scale), -scale, scale - 1).astype(np.int32)
    reconstructed = codes / scale
    return codes, reconstructed


def draw_graphs(audio, codes, reconstructed, rate, bits, filename):
    """Save the original waveform, samples, codes, and comparison."""
    n = len(audio)
    center = int(np.argmax(np.abs(audio)))
    count = min(120, n)
    start = max(0, min(center - count // 2, n - count))
    idx = np.arange(start, start + count)
    t = idx / rate

    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    axes[0].plot(np.arange(n) / rate, audio, linewidth=0.7)
    axes[0].set_title("1. Original audio waveform")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Amplitude")

    axes[1].plot(t, audio[idx], alpha=0.5)
    axes[1].stem(t, audio[idx], linefmt="C1-", markerfmt="C1o", basefmt="k-")
    axes[1].set_title("2. Samples (input audio is already digital)")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Amplitude")

    axes[2].step(t, codes[idx], where="mid", color="C2")
    axes[2].set_title(f"3. Signed {bits}-bit PCM codes")
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylabel("PCM code")

    axes[3].plot(t, audio[idx], label="Original")
    axes[3].step(t, reconstructed[idx], where="mid", label=f"{bits}-bit quantized")
    axes[3].set_title("4. Original vs. quantized")
    axes[3].set_xlabel("Time (s)")
    axes[3].set_ylabel("Amplitude")
    axes[3].legend()

    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Simple audio quantization")
    parser.add_argument("--bits", type=int, default=4, help="PCM bit depth, e.g. 4 or 16")
    parser.add_argument("--audio", default="audio/Drone_Sound(1).mp3", help="MP3/WAV path")
    args = parser.parse_args()

    audio, rate = load_audio(args.audio)
    if len(audio) == 0:
        raise ValueError("The audio file is empty.")
    codes, reconstructed = quantize(audio, args.bits)
    mse = np.mean((audio - reconstructed) ** 2)

    folder = Path("results")
    folder.mkdir(exist_ok=True)
    image_file = folder / f"graphs_{args.bits}bit.png"
    audio_file = folder / f"quantized_{args.bits}bit.wav"
    draw_graphs(audio, codes, reconstructed, rate, args.bits, image_file)
    # PCM_24 stores 1–24-bit quantized values without further 16-bit rounding.
    sf.write(audio_file, reconstructed, rate, subtype="PCM_24")

    print(f"Audio: {args.audio}")
    print(f"Sample rate: {rate} Hz")
    print(f"Samples: {len(audio)}")
    print(f"Duration: {len(audio) / rate:.3f} seconds")
    print(f"Sampling interval: {1 / rate:.8f} seconds")
    print(f"Bits: {args.bits} | Levels: {2 ** args.bits}")
    print(f"MSE: {mse:.10g}")
    print("\nSample | Amplitude | PCM code | Binary")
    center = int(np.argmax(np.abs(audio)))
    start = max(0, center - 10)
    for i in range(start, min(start + 20, len(audio))):
        binary = format(int(codes[i]) & ((1 << args.bits) - 1), f"0{args.bits}b")
        print(f"{i + 1:6d} | {audio[i]:+.8f} | {codes[i]:+8d} | {binary}")
    print(f"\nSaved graphs: {image_file}")
    print(f"Saved WAV: {audio_file}")


if __name__ == "__main__":
    main()
