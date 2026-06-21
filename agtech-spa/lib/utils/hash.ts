export function hash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function mockNdvi(seed: string): number {
  const s = hash(seed);
  return Math.round((0.15 + (s % 70) / 100) * 1000) / 1000;
}

export function mockHumedadSuelo(seed: string): number {
  const s = hash(seed);
  return Math.round((15 + (s % 60)) * 10) / 10;
}
