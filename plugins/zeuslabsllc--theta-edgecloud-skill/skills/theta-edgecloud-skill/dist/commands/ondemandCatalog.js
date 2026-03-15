// Reference fallback catalog for when live on-demand service discovery is unavailable.
export const ONDEMAND_SERVICE_CATALOG = {
    flux: {
        slug: 'flux',
        category: 'ImageGen',
        requiredInputFields: ['prompt'],
        supportsInputPresignedUrls: false,
        observedUnitPriceUsd: '0.01 / image'
    },
    blip: {
        slug: 'blip',
        category: 'ImageCaption',
        requiredInputFields: ['input_img'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.01 / image',
        notes: 'Prefer presigned upload to avoid external URL fetch failures.'
    },
    esrgan: {
        slug: 'esrgan',
        category: 'ImageRestore',
        requiredInputFields: ['input_img'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.02 / image'
    },
    voice_cloning: {
        slug: 'voice_cloning',
        category: 'TextToSpeech',
        requiredInputFields: ['text', 'language', 'voice'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.01 / audio'
    },
    instant_id: {
        slug: 'instant_id',
        category: 'ImageGen',
        requiredInputFields: ['face_img', 'prompt'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.24 / image'
    },
    grounding_dino: {
        slug: 'grounding_dino',
        category: 'ObjectDetection',
        requiredInputFields: ['input_img', 'detection_prompt'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.01 / image'
    },
    talking_head: {
        slug: 'talking_head',
        category: 'VideoGen',
        requiredInputFields: ['img', 'audio'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: '0.02 / video'
    },
    whisper: {
        slug: 'whisper',
        category: 'SpeechRec',
        requiredInputFields: ['audio_filename'],
        supportsInputPresignedUrls: true,
        observedUnitPriceUsd: 'low fractional / clip'
    },
    step_video: {
        slug: 'step_video',
        category: 'VideoGen',
        requiredInputFields: ['prompt'],
        supportsInputPresignedUrls: false,
        observedUnitPriceUsd: '0.20 / video',
        notes: 'Often asynchronous and long-running.'
    },
    stable_viton: {
        slug: 'stable_viton',
        category: 'VirtualTryOn',
        requiredInputFields: ['input_img', 'cloth_img'],
        supportsInputPresignedUrls: true
    },
    stable_diffusion_turbo_vision: {
        slug: 'stable_diffusion_turbo_vision',
        category: 'ImageGen',
        requiredInputFields: ['prompt'],
        supportsInputPresignedUrls: false
    },
    stable_diffusion_xl_lightning: {
        slug: 'stable_diffusion_xl_lightning',
        category: 'ImageGen',
        requiredInputFields: ['prompt'],
        supportsInputPresignedUrls: false
    },
    stable_diffusion_xl_turbo: {
        slug: 'stable_diffusion_xl_turbo',
        category: 'ImageGen',
        requiredInputFields: ['prompt'],
        supportsInputPresignedUrls: false
    },
    llama_3_8b: {
        slug: 'llama_3_8b',
        category: 'LLM',
        requiredInputFields: ['messages'],
        supportsInputPresignedUrls: false
    },
    llama_3_1_70b: {
        slug: 'llama_3_1_70b',
        category: 'LLM',
        requiredInputFields: ['messages'],
        supportsInputPresignedUrls: false,
        notes: 'Observed occasional 409: No instances available.'
    }
};
export function listOnDemandServices() {
    return Object.values(ONDEMAND_SERVICE_CATALOG);
}
