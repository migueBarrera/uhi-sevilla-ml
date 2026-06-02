export async function predictTemperature(payload) {
  const endpoint = 'https://predict-temperature-bzqfrud2ua-ew.a.run.app';
  console.log('[Predict Service]', new Date().toISOString(), '-> sending payload:', payload);
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    let json = null;
    try {
      json = await res.json();
    } catch (parseErr) {
      console.error('[Predict Service]', new Date().toISOString(), '-> failed to parse JSON response', parseErr);
    }

    console.log('[Predict Service]', new Date().toISOString(), '-> response status:', res.status, 'body:', json);

    const predictedArray = extractPredictions(json);
    if (predictedArray.length > 0) {
      const firstValue = Number(predictedArray[0]);
      return { success: true, predicted: firstValue, predicted_array: predictedArray, raw: json, status: res.status };
    }

    return { success: false, predicted: null, raw: json, status: res.status };
  } catch (err) {
    console.error('[Predict Service] Error', new Date().toISOString(), err);
    return { success: false, error: err };
  }
}

function extractPredictions(json) {
  if (!json) return [];

  if (Array.isArray(json)) {
    return json.map(v => Number(v)).filter(v => !Number.isNaN(v));
  }

  const candidates = [
    json.temperaturas_predichas,
    json.predictions,
    json.predicted,
    json.values,
    json.data,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate)) {
      const nums = candidate.map(v => Number(v)).filter(v => !Number.isNaN(v));
      if (nums.length > 0) return nums;
    }
  }

  return [];
}
