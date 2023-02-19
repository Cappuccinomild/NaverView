# NaverView
1. 크롤러

    1) 검색어 입력 양식

        input.txt
        신어
        이형태1 이형태2 이형태3

        신어
        이형태1 이형태2 이형태3

        신어
        이형태1 이형태2 이형태3
        -->이형태 끼리는 탭으로 구분합니다.

    2) 저장 형식

        링크 추출 -> 본문 추출 순서로 진행됩니다.

        링크는 link.db 파일에 저장되고 만약 같은 링크가 파일내에 있다면 저장하지 않습니다.
        *'이형태1' 에서 찾은 블로그 링크와 '이형태2' 에서 찾은 블로그 링크가 같다면 둘 중 먼저 찾은 이형태의 카테고리로 저장합니다.

        링크저장 형식 : 신어    이형태      블로그,카페 이름     작성 날짜      링크        본문 검색여부

    3) 본문 크롤러

        link.db 파일에서 링크를 불러와 블로그, 카페 본문을 크롤링 합니다.
        이때 저장된링크의 본문 검색여부 카테고리에 본문을 검색 성공했을경우 성공했음을 표시합니다.
        본문 크롤러에는 따로 검색어를 넣을 필요 없이 link.db에서 본문 검색여부를 확인해 크롤링합니다.

        크롤링된 본문역시 link.db에 저장될 예정입니다.
        본문 저장 형식 : 신어       이형태      블로그,카페 이름    작성 날짜   링크    본문

    * .db -> .txt 변환기
        .db 는 일반 메모장으로 확인이 불가능한 확장자 입니다. 검색기에 사용하기 위해 link.db 내의 저장된 본문을 아래 형식으로 출력하는 프로그램을 제작합니다.
        파일 계층
        신어 -> 이형태 -> 월별
        검색기에 사용하시려면 txt 파일로 변환 후 사용하시면 됩니다.


2. 검색기

    1) 앞 뒤 문장 검색기

        앞 뒤 n 문장과 키워드를 출력함
        검색어는 여러개를 받아오며 문장구분은 '.'을 기준으로 구분합니다.
        블로그나 카페는 작성 형식에따라 문장이 잘 구분되지 않을 수 있습니다.
        최대 문장은 10개로 가정하여 프로그램 제작할 예정입니다.

    2) 출력 형식

        출력 형식은
        신어    이형태  -n번째 문장 ~ +n번째 문장
        으로 계획하고있으나 출력 파일에 더 필요하신 부분 있으면 말씀 해 주십시오.


3. 통계

    1) 출력 형식

        이형태별 월별통계
        이형태별 전체통계
        신어 월별통계
        전체통계
        형식의 csv 파일 출력

    2) 작동 방식

        크롤링 시에 관련없는 본문이 크롤링 되는 경우가 많기 때문에
        link.db에 저장된 본문을 활용해서 본문에 정말 키워드가 존재하는지 확인합니다.
        본문에서 검색하는 이형태와 일치하는 부분이 있는지 검사합니다. 공백을 구분합니다.
        ex)무민 세대 와 무민세대는 다른 카테고리