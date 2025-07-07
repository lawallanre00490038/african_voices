# import os
# import numpy as np
# import librosa
# import soundfile as sf
# import noisereduce as nr

# # def calculate_snr(signal, noise):
# #     signal_power = np.mean(signal ** 2)
# #     noise_power = np.mean(noise ** 2)

# #     if noise_power == 0:
# #         return float('inf')
# #     return 10 * np.log10(signal_power / noise_power)


# def calculate_snr(signal, noise, eps=1e-10):
#     signal_power = np.mean(signal ** 2)
#     noise_power = np.mean(noise ** 2)

#     if noise_power < eps:
#         print("Warning: Noise power is zero or near zero — cannot compute realistic SNR.")
#         return float('inf')
#     return 10 * np.log10(signal_power / noise_power)


# def process_audio_optimize_snr(input_path):
#     data, sr = librosa.load(input_path, sr=None)

#     # Detect non-silent regions
#     non_silent_intervals = librosa.effects.split(data, top_db=30)
#     if len(non_silent_intervals) == 0:
#         print("Audio appears to be silent.")
#         return None

#     # Use first non-silent segment as signal
#     signal_start, signal_end = non_silent_intervals[0]
#     signal = data[signal_start:signal_end]

#     # Use noise before signal starts
#     noise = data[:signal_start] if signal_start > 0 else data[:1000]

#     snr_before = calculate_snr(signal, noise)
#     print(f"Initial SNR: {snr_before:.2f} dB")

#     # Case 1: Very noisy audio
#     if snr_before < 30:
#         print("Noise audio")
#         print(f"SNR: {snr_before:.2f} dB")
#         return None

#     # Case 2: Clean enough — no need to reduce
#     elif snr_before >= 38.5 and snr_before < 49:
#         print("Acceptable audio — no need for noise reduction.")
#         print(f"SNR: {snr_before:.2f} dB")
#         return None

#     # Case 3: Needs enhancement
#     elif 30 <= snr_before < 38.5:
#         print("Moderate audio — trying to improve with noise reduction...")
#         prop = 0.2
#         max_prop = 1.0
#         improved_audio = data
#         prev_snr = snr_before

#         while prop <= max_prop:
#             reduced = nr.reduce_noise(y=improved_audio, sr=sr, y_noise=noise, prop_decrease=prop)
#             new_signal = reduced[signal_start:signal_end]
#             snr_now = calculate_snr(new_signal, noise)

#             print(f"Trying prop_decrease={prop:.2f} → SNR: {snr_now:.2f} dB")

#             if snr_now >= 40:
#                 base, ext = os.path.splitext(input_path)
#                 output_path = base + "_processed" + ext
#                 sf.write(output_path, reduced, sr)
#                 print(f"Audio fine-tuned and saved to {output_path}")
#                 return output_path

#             if snr_now <= prev_snr:
#                 break  # No improvement anymore

#             improved_audio = reduced
#             prev_snr = snr_now
#             prop += 0.2

#         print("Tried noise reduction but couldn't reach 40 dB SNR.")
#         return None

#     # Case 4: Already very clean
#     else:  # snr_before >= 49
#         print("Good audio")
#         print(f"SNR: {snr_before:.2f} dB")
#         return None

# # Example usage
# process_audio_optimize_snr("./input/test3.wav")





import os
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr

def calculate_snr(signal, noise, eps=1e-10):
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power < eps:
        print("⚠️ Noise power is zero or near zero — cannot compute realistic SNR.")
        return float('inf')
    return 10 * np.log10(signal_power / noise_power)

def select_valid_noise(data, signal_start, signal_end):
    """Try fallback noise regions."""
    for region_name, noise in [
        ("before signal", data[:signal_start]),
        ("after signal", data[signal_end:signal_end+1000]),
        ("middle of audio", data[len(data)//2:len(data)//2+1000])
    ]:
        if len(noise) > 0 and np.std(noise) >= 1e-6:
            print(f"✅ Using noise from: {region_name}")
            return noise
    print("⚠️ All noise segments are too quiet.")
    return data[:1000]  # fallback anyway

def process_audio_optimize_snr(input_path):
    data, sr = librosa.load(input_path, sr=None)

    # Detect non-silent regions
    non_silent_intervals = librosa.effects.split(data, top_db=30)
    if len(non_silent_intervals) == 0:
        print("❌ Audio appears to be silent.")
        return None

    # Use first non-silent segment as signal
    signal_start, signal_end = non_silent_intervals[0]
    signal = data[signal_start:signal_end]

    # Select noise intelligently
    noise = select_valid_noise(data, signal_start, signal_end)
    print(f"🔍 Noise stats — std: {np.std(noise):.6f}, mean: {np.mean(noise):.6f}")

    snr_before = calculate_snr(signal, noise)
    print(f"📈 Initial SNR: {snr_before:.2f} dB")

    # Case: SNR not computable
    if not np.isfinite(snr_before):
        print("⚠️ SNR is infinite or undefined — cannot process.")
        return None

    # Case: Very noisy audio
    if snr_before < 30:
        print("❌ Noise audio — below threshold.")
        return None

    # Case: Clean enough
    elif 38.5 <= snr_before < 49:
        print("✅ Acceptable audio — no need for noise reduction.")
        return None

    # Case: Already very clean
    elif snr_before >= 49:
        print("✅ Good audio — SNR is high.")
        return None

    # Case: Needs improvement
    print("🛠️ Moderate audio — attempting noise reduction...")
    prop = 0.2
    max_prop = 1.0
    improved_audio = data
    prev_snr = snr_before

    while prop <= max_prop:
        reduced = nr.reduce_noise(y=improved_audio, sr=sr, y_noise=noise, prop_decrease=prop)
        new_signal = reduced[signal_start:signal_end]
        snr_now = calculate_snr(new_signal, noise)

        print(f"🔁 Trying prop_decrease={prop:.2f} → SNR: {snr_now:.2f} dB")

        if snr_now > prev_snr:
            base, ext = os.path.splitext(input_path)
            output_path = base + "_processed" + ext
            sf.write(output_path, reduced, sr)
            print(f"✅ Audio improved and saved to {output_path}")
            return output_path

        if snr_now <= prev_snr:
            print("⚠️ No improvement in SNR — stopping.")
            break

        improved_audio = reduced
        prev_snr = snr_now
        prop += 0.2

    print("❌ Could not improve SNR above threshold.")
    return None

# Example usage
process_audio_optimize_snr("./audio/noise.wav")
