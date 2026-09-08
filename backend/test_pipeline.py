from app.services.audio_processor import load_and_preprocess_audio
from app.services.feature_extractor import extract_features
from app.services.voice_detector import get_voice_detector
from app.services.context_analyzer import analyze_context
from app.services.risk_engine import get_risk_breakdown
from app.services.prevention_engine import get_prevention_response

audio, sr = load_and_preprocess_audio('test_audio.wav')
features = extract_features(audio, sr)
detector = get_voice_detector()
human_prob, ai_prob = detector.predict(features)

context = analyze_context(
    transcript='This is your bank calling, urgent, please share the OTP immediately',
    transaction_amount=50000,
)

breakdown = get_risk_breakdown(ai_prob, context['context_risk_points'])
prevention = get_prevention_response(breakdown['risk_level'])

print(f'Human Voice Probability: {human_prob*100:.1f}%')
print(f'AI Generated Probability: {ai_prob*100:.1f}%')
print(f'Risk Score: {breakdown["final_risk_score"]}/100')
print(f'Risk Level: {breakdown["risk_level"]}')
print(f'Context Indicators: {context["indicators"]}')
print(f'Recommendation: {prevention["recommendation"]}')
print('Actions:')
for action in prevention['actions']:
    print(f'  - {action}')