"""scripts/leaderboard.py on CPU: checks HTML/Liquid sanitization, table cell escaping, single-stream vs batched
filtering, speculative decoding detection from flags and command snippets, best-per-setup deduplication, and --help."""
import importlib.util
import pathlib
import subprocess
import sys

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "leaderboard.py"
spec = importlib.util.spec_from_file_location("leaderboard", SCRIPT)
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)


def test_safe_and_cell_strip_html_liquid_and_escape_pipes():
    evil = '<script>alert(1)</script> {{ site.secret }} {% include x %} {% endraw %} | [link]\nbreak'
    out = lb.safe(evil)
    assert "<script>" not in out and "{{" not in out and "{%" not in out and "endraw" not in out.lower()
    c = lb.cell(evil)
    assert "\\|" in c and "\\[" in c and "\\]" in c and "\n" not in c


def test_help_flag_prints_usage_and_writes_no_file(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "Usage: python3 scripts/leaderboard.py" in r.stdout
    assert not list(tmp_path.iterdir())


def test_spec_detects_flags_and_command_snippets():
    assert lb.spec({"engineFlags": {"mtpEnabled": True}}) == "MTP"
    assert lb.spec({"engineFlags": {"specDecoding": True, "specMethod": "draft-dflash"}}) == "draft-dflash"
    assert lb.spec({"engineFlags": {"commandSnippet": 'vllm serve x --speculative-config \'{"method":"mtp"}\''}}) == "MTP (cmd)"
    assert lb.spec({"engineFlags": {"commandSnippet": "llama-server --spec-type draft -md d.gguf"}}) == "spec (cmd)"
    assert lb.spec({"engineFlags": {}}) == ""


def test_best_per_setup_keeps_fastest_and_separates_streams():
    runs = [
        {"id": "1", "status": "APPROVED", "tokSOut": 110.0, "batchSize": 1,
         "hardware": {"gpuName": "Intel Arc Pro B70", "gpuCount": 1},
         "model": {"hfId": "Qwen/Qwen3.8-27B"}, "engine": {"engineName": "vLLM", "quantization": "GPTQ-Int4"}},
        {"id": "2", "status": "APPROVED", "tokSOut": 125.0, "batchSize": 1,
         "hardware": {"gpuName": "Intel Arc Pro B70", "gpuCount": 1},
         "model": {"hfId": "Qwen/Qwen3.8-27B"}, "engine": {"engineName": "vLLM", "quantization": "GPTQ-Int4"}},
        {"id": "3", "status": "APPROVED", "tokSOut": 1500.0, "batchSize": 64, "engineFlags": {"concurrency": 64},
         "hardware": {"gpuName": "Intel Arc Pro B70", "gpuCount": 1},
         "model": {"hfId": "Qwen/Qwen3.6-35B-A3B"}, "engine": {"engineName": "vLLM", "quantization": "GPTQ-Int4"}},
    ]
    one = lb.best_per_setup([r for r in runs if lb.single_stream(r)])
    batched = lb.best_per_setup([r for r in runs if not lb.single_stream(r)])
    assert len(one) == 1 and one[0]["id"] == "2"
    assert len(batched) == 1 and batched[0]["id"] == "3"
