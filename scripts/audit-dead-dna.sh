#!/usr/bin/env bash
# spec-verified: code.claude.com/docs 2026-05-11
# Capability registry audit for the Meta-Harness Zero Dead DNA rule.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

shopt -s nullglob
registries=(analysis/capabilities/*-capability-registry.yaml)

if [ "${#registries[@]}" -eq 0 ]; then
  echo "audit-dead-dna: no capability registries found"
  exit 1
fi

if ! command -v ruby >/dev/null 2>&1; then
  echo "audit-dead-dna: ruby is required for YAML validation"
  exit 1
fi

ruby - "${registries[@]}" <<'RUBY'
require "yaml"
require "date"

ALLOWED_STATES = %w[ACTIVE DEFERRED BLOCKED].freeze
ALLOWED_DEFERRED_REASONS = %w[
  awaiting-upstream-dep
  awaiting-api-key
  cost-prohibitive
  experimental-upstream
  out-of-scope-for-current-phase
  redundant-with-other-tool
].freeze
REQUIRED_HEADER = %w[
  tool
  tool_version
  canonical_docs
  last_harvested
  harvested_by
  capabilities
].freeze
REQUIRED_ROW = %w[id surface name state description].freeze

def present?(value)
  case value
  when nil
    false
  when String
    !value.strip.empty?
  when Array, Hash
    !value.empty?
  else
    true
  end
end

errors = []
summary = Hash.new(0)

ARGV.each do |path|
  begin
    data = YAML.safe_load(File.read(path), permitted_classes: [Date], aliases: true)
  rescue StandardError => e
    errors << "#{path}: YAML parse failed: #{e.class}: #{e.message}"
    next
  end

  unless data.is_a?(Hash)
    errors << "#{path}: registry root must be a mapping"
    next
  end

  missing_header = REQUIRED_HEADER.reject { |key| data.key?(key) }
  errors << "#{path}: missing header keys: #{missing_header.join(', ')}" unless missing_header.empty?

  caps = data["capabilities"]
  unless caps.is_a?(Array)
    errors << "#{path}: capabilities must be a list"
    next
  end

  if caps.empty?
    if data["spec-verified"] == false
      summary["BOOTSTRAP_EMPTY"] += 1
      next
    end
    errors << "#{path}: capabilities is empty without spec-verified: false bootstrap marker"
    next
  end

  caps.each_with_index do |cap, index|
    label = "#{path}:capabilities[#{index}]"
    unless cap.is_a?(Hash)
      errors << "#{label}: row must be a mapping"
      next
    end

    missing_row = REQUIRED_ROW.reject { |key| present?(cap[key]) }
    errors << "#{label}: missing required fields: #{missing_row.join(', ')}" unless missing_row.empty?

    state = cap["state"].to_s
    unless ALLOWED_STATES.include?(state)
      errors << "#{label}: invalid state #{state.inspect}; expected #{ALLOWED_STATES.join('|')}"
      next
    end

    summary[state] += 1

    case state
    when "ACTIVE"
      %w[wired_at invoked_by].each do |key|
        errors << "#{label}: ACTIVE row missing #{key}" unless present?(cap[key])
      end
    when "DEFERRED"
      %w[reason target_phase tracking_issue].each do |key|
        errors << "#{label}: DEFERRED row missing #{key}" unless present?(cap[key])
      end
      reason = cap["reason"].to_s
      if present?(reason) && !ALLOWED_DEFERRED_REASONS.include?(reason)
        errors << "#{label}: DEFERRED reason #{reason.inspect} is not allowed"
      end
    when "BLOCKED"
      %w[blocker blocker_resolution_path].each do |key|
        errors << "#{label}: BLOCKED row missing #{key}" unless present?(cap[key])
      end
    end
  end
end

if errors.any?
  warn "audit-dead-dna: capability registry violations"
  errors.each { |error| warn "  - #{error}" }
  exit 1
end

puts "audit-dead-dna: OK"
puts "  registries=#{ARGV.length}"
puts "  active=#{summary['ACTIVE']}"
puts "  deferred=#{summary['DEFERRED']}"
puts "  blocked=#{summary['BLOCKED']}"
puts "  bootstrap_empty=#{summary['BOOTSTRAP_EMPTY']}"
RUBY
