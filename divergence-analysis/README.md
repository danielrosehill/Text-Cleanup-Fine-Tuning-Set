# Divergence Analysis

This directory contains analyses of the divergences between different cleanup approaches for individual samples.

## Purpose

These analyses examine the actual differences between:
- Raw Whisper transcripts (verbatim ASR output)
- Auto-cleanup attempts (where applicable, e.g., Sample 1 with Gemini)
- Manual cleanup (ground truth)

## What's Analyzed

For each sample with divergence analysis:
- Character and word-level differences
- Structural changes (paragraphing, sentence breaks)
- Stylistic patterns and editing choices
- Quantitative metrics
- Key principles demonstrated by the manual cleanup

## Files

- **sample-1-analysis.md** - Comparison of Whisper → Gemini auto-cleanup → Manual cleanup for the first sample, demonstrating why fine-tuning is needed

## Distinction from AI Analysis

- **This folder (divergence-analysis/)**: Analyzes actual sample data and editing patterns
- **ai-analysis/**: Planning and strategy for fine-tuning (model selection, sample sizes, dataset structure)
