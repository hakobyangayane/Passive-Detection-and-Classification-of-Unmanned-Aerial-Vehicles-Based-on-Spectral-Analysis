# Audio Digitalization

A Python project for processing and analyzing digital audio signals. The program supports MP3 and WAV files and applies PCM quantization with different bit depths.

The project includes 4-bit and 16-bit quantization examples to compare the effects of bit depth on signal precision and quantization error.

## Features

- Load MP3 and WAV audio files
- Apply PCM quantization using different bit depths
- Visualize audio waveforms and sampled values
- Display PCM codes and their binary representations
- Compare original and quantized audio signals
- Calculate Mean Squared Error (MSE)
- Save graphs and quantized audio files

## Technologies

- Python
- NumPy
- Matplotlib
- SoundFile
- imageio-ffmpeg

## Installation

Install the required Python libraries:

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the program with 4-bit quantization:

```bash
python audio_digitalization.py --bits 4
```

Run the program with 16-bit quantization:

```bash
python audio_digitalization.py --bits 16
```

To process a different audio file:

```bash
python audio_digitalization.py --audio "audio/example_audio.wav" --bits 8
```

Replace `audio/example_audio.wav` with the path to your audio file.

## Results

The program saves the generated files in the `results` directory.

The output includes:

- A PNG image with four signal analysis graphs
- A WAV file containing the quantized audio
- PCM codes and binary representations displayed in the terminal
- Mean Squared Error (MSE) displayed in the terminal

The graphs show the original waveform, audio samples, PCM codes, and a comparison between the original and quantized signals.