--------------------------- MODULE ProductLoop ---------------------------
EXTENDS Naturals
CONSTANTS ForgeWhole, DropUnknown, MutateFrozen
VARIABLES phase, admitted, coverage, effectKnown, effectSent, frozen,
          requestUnchanged, ownerAccepted, wholeClosed
vars == <<phase, admitted, coverage, effectKnown, effectSent, frozen,
          requestUnchanged, ownerAccepted, wholeClosed>>
Init == /\ phase = "admission" /\ admitted = FALSE /\ coverage = FALSE
        /\ effectKnown = TRUE /\ effectSent = FALSE /\ frozen = TRUE
        /\ requestUnchanged = TRUE /\ ownerAccepted = FALSE /\ wholeClosed = FALSE
Admit == /\ phase = "admission" /\ phase' = "reconcile" /\ admitted' = TRUE
         /\ UNCHANGED <<coverage, effectKnown, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
NeedScope == /\ phase = "reconcile" /\ phase' = "semantic"
             /\ UNCHANGED <<admitted, coverage, effectKnown, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
SelectScope == /\ phase = "semantic" /\ phase' = "next" /\ coverage' = TRUE
               /\ UNCHANGED <<admitted, effectKnown, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
ConsumeNext == /\ phase = "next" /\ admitted /\ coverage /\ phase' = "verification"
               /\ effectSent' = TRUE /\ requestUnchanged' = ~MutateFrozen
               /\ UNCHANGED <<admitted, coverage, effectKnown, frozen, ownerAccepted, wholeClosed>>
Interrupt == /\ phase = "verification" /\ phase' = "unknown" /\ effectKnown' = FALSE
             /\ UNCHANGED <<admitted, coverage, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
ReadOriginal == /\ phase = "unknown" /\ phase' = "verification" /\ effectKnown' = TRUE
                /\ UNCHANGED <<admitted, coverage, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
BadReplay == /\ phase = "unknown" /\ DropUnknown /\ phase' = "bad_replay"
             /\ UNCHANGED <<admitted, coverage, effectKnown, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
AcceptLocal == /\ phase = "verification" /\ effectKnown /\ phase' = "delivery"
               /\ ownerAccepted' = TRUE /\ wholeClosed' = ForgeWhole
               /\ UNCHANGED <<admitted, coverage, effectKnown, effectSent, frozen, requestUnchanged>>
Deliver == /\ phase = "delivery" /\ phase' = "outer"
           /\ UNCHANGED <<admitted, coverage, effectKnown, effectSent, frozen, requestUnchanged, ownerAccepted, wholeClosed>>
Stop == /\ phase \in {"outer", "bad_replay"} /\ UNCHANGED vars
Next == Admit \/ NeedScope \/ SelectScope \/ ConsumeNext \/ Interrupt \/ ReadOriginal \/ BadReplay \/ AcceptLocal \/ Deliver \/ Stop
Spec == Init /\ [][Next]_vars
AdmittedEffects == effectSent => (admitted /\ coverage)
FrozenPreserved == frozen => requestUnchanged
UnknownReadOnly == phase # "bad_replay"
LocalCannotCloseWhole == ~wholeClosed
=============================================================================
