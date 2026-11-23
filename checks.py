"""고정 벡터로 구현을 검사합니다. 실제 모델 품질 검사가 아닙니다."""
import copy
import math

from pydantic import ValidationError

import support


class FixedEmbedder:
    def __init__(self):
        self.calls = []

    def encode(self, texts, normalize_embeddings=True):
        self.calls.extend(texts)
        assert normalize_embeddings is True, "문서와 질문 벡터를 정규화하세요."
        vectors = []
        for text in texts:
            vector = [float(word in text) for word in ("VPN", "토큰", "출입", "Python")]
            if not any(vector):
                vector = [0.0, 0.0, 1.0, 0.0]
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append([value / norm for value in vector])
        return vectors


def must_raise(call):
    try:
        call()
    except (ValueError, ValidationError):
        return
    raise AssertionError("잘못된 입력을 거절하지 않았습니다.")


def run(api, stage):
    cases = []
    def check(name, function):
        try:
            function()
            cases.append({"name": name, "status": "통과", "detail": ""})
        except NotImplementedError as error:
            cases.append({"name": name, "status": "미완료", "detail": str(error)})
        except Exception as error:
            cases.append({"name": name, "status": "실패", "detail": f"{type(error).__name__}: {error}"})

    def chunks_check():
        documents = support.load_documents()
        original = copy.deepcopy(documents)
        chunks = api["prepare_chunks"](documents)
        assert len(chunks) == 8, "정제 후 청크는 8개입니다."
        assert len({row["chunk_id"] for row in chunks}) == 8
        assert documents == original, "입력 자료를 수정하지 마세요."
        assert all(row["text"].strip() and "KANT NEXT | 내부 문서" not in row["text"] for row in chunks)
        assert next(row for row in chunks if row["chunk_id"] == "vpn:0")["source"] == "devdesk://vpn/current"
        tiny = [{**documents[0], "paragraphs": ["  A\n B  ", "A B", " ", "KANT NEXT | 내부 문서", "C"]}]
        assert [row["text"] for row in api["prepare_chunks"](tiny)] == ["A B", "C"]

    def index_check():
        chunks = api["prepare_chunks"](support.load_documents())
        embedder = FixedEmbedder()
        client = api["build_index"](chunks, embedder)
        try:
            assert client.count("devdesk").count == len(chunks)
            stored, _ = client.scroll("devdesk", limit=20, with_payload=True)
            assert {row.payload["chunk_id"] for row in stored} == {row["chunk_id"] for row in chunks}
            assert all(text.startswith("passage: ") for text in embedder.calls)
        finally:
            client.close()

    def search_check():
        chunks = api["prepare_chunks"](support.load_documents())
        embedder = FixedEmbedder()
        client = api["build_index"](chunks, embedder)
        try:
            rows = api["search"](client, embedder, "VPN 승인", "access", 5)
            assert len(rows) == 5
            assert all(row["status"] == "current" and row["category"] == "access" for row in rows)
            assert {r["document_id"] for r in rows} == {"vpn", "token", "door"}
            assert api["search"](client, embedder, "VPN", "missing", 1) == []
            assert len(api["search"](client, embedder, "Python", "development", 1)) == 1
            assert embedder.calls[-1].startswith("query: ")
            must_raise(lambda: api["search"](client, embedder, "VPN", "access", 0))
        finally:
            client.close()

    def rewrite_check():
        aliases = {"초록문": "VPN 원격 접속", "임시열쇠": "API 토큰"}
        assert api["rewrite_query"]("초록문과 임시열쇠 확인", aliases) == "VPN 원격 접속과 API 토큰 확인"
        assert api["rewrite_query"]("Python 버전", aliases) == "Python 버전"
        assert api["rewrite_query"]("초록문", {"초록문": "문서명"}) == "문서명"

    def answer_check():
        rows = [{"chunk_id": "doc:0", "text": "승인은 보안팀에 요청합니다."}]
        good = {"answer": "보안팀에 요청합니다.", "citations": ["doc:0"], "needs_human": False}
        seen = []
        def generate(question, context):
            seen.append((question, context))
            return good
        assert api["answer_question"]("승인 팀은?", rows, generate) == good
        assert seen == [("승인 팀은?", "[doc:0] 승인은 보안팀에 요청합니다.")]
        assert api["answer_question"]("자료 없음", [], lambda *a: 1)["needs_human"] is True
        for bad in ({**good, "citations": ["other:0"]}, {**good, "citations": []},
                    {**good, "needs_human": True}, {**good, "answer": " "}):
            must_raise(lambda b=bad: api["answer_question"]("질문", rows, lambda *a: b))
        held = {"answer": "기한을 확인할 자료가 없습니다.", "citations": [], "needs_human": True}
        assert api["answer_question"]("기한은?", rows, lambda *a: held) == held

    def golden_check():
        rows = support.validate_golden(api["make_golden"]())
        assert len(rows) == 2
        wrong = copy.deepcopy(rows)
        answerable = next(row for row in wrong if row["relevant_document_ids"])
        answerable["category"] = "wrong"
        must_raise(lambda: support.validate_golden(wrong))

    def comparison_check():
        chunks = api["prepare_chunks"](support.load_documents())
        embedder = FixedEmbedder()
        client = api["build_index"](chunks, embedder)
        seen = []
        def generate(question, context):
            seen.append(question)
            key = context.split("]", 1)[0][1:]
            return {"answer": "검사용 응답", "citations": [key], "needs_human": False}
        try:
            report = support.evaluate(api, client, embedder, generate)
            for case in report["cases"]:
                if case["relevant_document_ids"]:
                    assert seen.count(case["question"]) == 2, "검색만 바꾸고 생성에는 같은 원질문을 전달하세요."
            assert len(report["rows"]) == 8
        finally:
            client.close()

    def measure_check():
        case = {"relevant_document_ids": ["a", "b"], "required_terms": ["승인", "보안팀"]}
        rows = [{"document_id": "a"}, {"document_id": "a"}]
        reply = {"answer": "보안팀 승인", "needs_human": False, "citations": ["a:0"]}
        assert api["measure"](case, rows, reply) == {"document_recall": 0.5, "answer_check": True, "failure": "검색 누락"}
        rows.append({"document_id": "b"})
        assert api["measure"](case, rows, {**reply, "answer": "승인"})["failure"] == "답변 확인 필요"
        absent = {"relevant_document_ids": [], "required_terms": []}
        assert api["measure"](absent, [], reply) == {"document_recall": None, "answer_check": False, "failure": "보류 실패"}
        assert api["measure"](absent, [], {**reply, "needs_human": True})["failure"] == "없음"

    def challenge_check():
        a, b, c = ({"chunk_id": key, "text": key} for key in ("a", "b", "c"))
        rankings = [[a, a, b], [c, b]]
        original = copy.deepcopy(rankings)
        merged = api["fuse_rankings"](rankings, 3)
        assert [r["chunk_id"] for r in merged] == ["b", "a", "c"]
        assert math.isclose(merged[0]["score"], 2 / 62)
        assert rankings == original
        assert api["fuse_rankings"]([[], []], 2) == []
        must_raise(lambda: api["fuse_rankings"]([], 0))

    if stage in ("all", "index"):
        check("TXT/HTML 정제와 문단 청킹", chunks_check)
        check("임베딩 입력과 Qdrant 저장", index_check)
        check("현행/분류 필터와 검색 개수", search_check)
    if stage in ("all", "answer"):
        check("별칭을 사용하는 질의 변환", rewrite_check)
        check("출처 답변과 자료 없음 처리", answer_check)
    if stage in ("all", "evaluate"):
        check("직접 작성한 평가 사례", golden_check)
        check("문서 Recall과 답변 확인 분리", measure_check)
        check("변환 전후 생성 질문 고정", comparison_check)
    if stage == "challenge":
        check("RRF 중복, 동점, 입력 보존", challenge_check)
    return cases
