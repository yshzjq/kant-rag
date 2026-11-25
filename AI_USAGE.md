# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인을 확인할 때 사용할 수 있습니다. 미작성 빈칸, 과제 전체, 평가 사례나 선택 심화의 설계를 대신 완성해 달라고 요청하지 않습니다. 실제 실행 결과를 만들거나 고쳐 달라고 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적으세요. 사용했다면 필요한 만큼 기록하세요. API 키나 원문 개인정보를 대화에 넣지 않습니다.

사용 도구:
- Claude (Cowork). 빈칸별 개념 설명, 내가 작성한 코드의 오류 원인 확인, 저장된 main.py와 검사 오류 대조에 사용함. 이 AI_USAGE.md도 대화 내용을 바탕으로 AI가 초안을 쓰고 내가 확인함.

질문과 관련 함수:
- prepare_chunks: split(' ')과 인자 없는 split()의 차이, join 사용법. 청크 사전에 넣을 키, chunk_id에서 str과 int를 이어 붙일 때의 TypeError. 이유 주석은 직접 작성하고 사실관계(category와 status는 필터, chunk_id는 인용, source는 원문 위치)를 확인받음.
- build_index: 임베딩과 정규화 개념, PointStruct의 id/vector/payload 의미, numpy 배열을 리스트로 바꾸는 방법.
- search: Qdrant Filter가 파이썬에서 계산하는 값이 아니라 Qdrant에 넘기는 조건 객체라는 점, FieldCondition의 key(필드 이름 문자열)와 value(변수) 구분.
- rewrite_query: 문자열 치환 방법(사과/바나나 예시로 replace 확인).
- answer_question: context를 [chunk_id] 본문으로 만들고 빈 줄로 잇는 방법, any()와 리스트 컴프리헨션 순서, [조건]처럼 대괄호로 감싸면 항상 참이 되는 문제.
- make_golden: 필드 의미와 과제 조건 점검만 받음. 질문, 참고 답변, 확인 문구는 직접 정함. AI는 제공 사례와 겹치는지, 별칭 사용 여부, 원문 ID, 빈 reference_answer 같은 조건 위반만 지적함.
- measure: Recall과 Precision의 차이, 집합 교집합(&), 0으로 나누기를 피하는 조건식.

이해한 내용:
- 원문을 문단 단위로 공백 정리 중복 제거 같이 처리한 후에 Qdrant를 저장해서 질문에 따라 청크를 가져오는 것을 이해하였다
- 직접 질문과 답변을 만들어서 평가하는 방식을 직접 알았다.

직접 수정한 부분:
- 공백 정리: 여러 번 시도한 뒤 AI가 제시한 ' '.join(paragraph.split()) 형태를 콘솔에서 확인하고 반영함 (str.join(' ', paragraph.split())로 작성).
- PointStruct: 처음에 vector.tolist()를 쓴 뒤 check에서 'list' object has no attribute 'tolist' 오류가 남. 콘솔에서 list(), float()를 비교해 보고 [float(x) for x in vector]로 고침.
- 필터 코드를 build_index에 잘못 넣었던 것을 AI가 파일을 보고 지적함. 내가 이전에 작성한 PointStruct 줄과 Filter를 각각 원래 자리로 옮김.
- 출처 검사: any([c not in reply["citations"]] for c in allowed)에서 비교 대상과 반복 대상을 바꾸고 대괄호를 제거해 any(c not in allowed for c in reply["citations"])로 고침.
- measure: len(found) 분모를 len(expected)로 고치고, 조건식은 len(expected) != 0으로 직접 작성함. AI가 조건 자리에 expected를 쓰라고 알려 준 뒤 같은 뜻의 형태로 작성함.
- 저장하지 않은 상태로 검사를 실행해 두 번 실패함. AI가 디스크의 main.py를 보고 저장 문제임을 알려 줌.


