import { useEffect, useRef, useCallback, useMemo, useState } from "react";

function normalize(text) {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

function buildWakePatterns(assistantName, wakeWord) {
  const raw = [assistantName, wakeWord].filter(Boolean);
  const names = [...new Set(raw.map(normalize))];
  return names.filter((n) => n.length >= 2);
}

function containsWakeWord(text, patterns) {
  const lower = normalize(text);
  return patterns.some((p) => lower.includes(p));
}

function extractCommand(text, patterns) {
  let cmd = text;
  for (const p of patterns) {
    const re = new RegExp(`(hola|hey|oye|ok)?\\s*${p}\\s*[,.:;-]?`, "gi");
    cmd = cmd.replace(re, " ");
  }
  return cmd.replace(/\s+/g, " ").trim();
}

export function useAlwaysListening({
  assistantName = "Yarbis",
  wakeWord = "Yarbis",
  enabled = true,
  onCommand,
  onWake,
  onError,
}) {
  const [listening, setListening] = useState(false);
  const [awaitingCommand, setAwaitingCommand] = useState(false);
  const recognitionRef = useRef(null);
  const enabledRef = useRef(enabled);
  const awaitingRef = useRef(false);
  const processingRef = useRef(false);
  const patterns = useMemo(() => buildWakePatterns(assistantName, wakeWord), [assistantName, wakeWord]);

  useEffect(() => {
    enabledRef.current = enabled;
  }, [enabled]);

  useEffect(() => {
    awaitingRef.current = awaitingCommand;
  }, [awaitingCommand]);

  const startRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !enabledRef.current) return;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        /* ignore */
      }
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "es-CO";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => {
      setListening(false);
      if (enabledRef.current && !processingRef.current) {
        setTimeout(() => startRecognition(), 400);
      }
    };
    recognition.onerror = (event) => {
      if (event.error === "not-allowed") {
        onError?.("Permite el micrófono para que pueda escucharte.");
        enabledRef.current = false;
      }
    };

    recognition.onresult = (event) => {
      const last = event.results[event.results.length - 1];
      if (!last.isFinal) return;
      const text = last[0].transcript.trim();
      if (!text || processingRef.current) return;

      const hasWake = containsWakeWord(text, patterns);
      const command = extractCommand(text, patterns);

      if (hasWake && command.length >= 3) {
        processingRef.current = true;
        setAwaitingCommand(false);
        onCommand?.(command, text);
        return;
      }

      if (hasWake && command.length < 3) {
        setAwaitingCommand(true);
        onWake?.();
        return;
      }

      if (awaitingRef.current) {
        processingRef.current = true;
        setAwaitingCommand(false);
        onCommand?.(text, text);
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
    } catch {
      /* already started */
    }
  }, [patterns, onCommand, onWake, onError]);

  const stopListening = useCallback(() => {
    enabledRef.current = false;
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setListening(false);
    setAwaitingCommand(false);
  }, []);

  const resumeListening = useCallback(() => {
    enabledRef.current = true;
    processingRef.current = false;
    startRecognition();
  }, [startRecognition]);

  const markProcessingDone = useCallback(() => {
    processingRef.current = false;
    if (enabledRef.current) startRecognition();
  }, [startRecognition]);

  useEffect(() => {
    if (enabled) {
      enabledRef.current = true;
      startRecognition();
    } else {
      stopListening();
    }
    return () => {
      enabledRef.current = false;
      recognitionRef.current?.stop();
    };
  }, [enabled, startRecognition, stopListening]);

  return { listening, awaitingCommand, stopListening, resumeListening, markProcessingDone };
}
