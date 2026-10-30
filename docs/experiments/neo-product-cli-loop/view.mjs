export const title = 'Neo product CLI | whole Goal remains open';
export const state = v => v.phase;
export const step = action => ({Admit:'original admission', NeedScope:'read full Goal and Owner evidence', SelectScope:'Session selects applicable clauses', ConsumeNext:'consume original next', Interrupt:'effect response missing', ReadOriginal:'read original Owner only', BadReplay:'replay without effect evidence', AcceptLocal:'original local acceptance', Deliver:'return original delivery and remaining Goal'})[action] ?? null;
