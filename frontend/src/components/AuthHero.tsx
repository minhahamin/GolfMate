import golferRabbit from '../assets/golfer-rabbit.png';

// 로그인/회원가입 페이지 좌측에 쓰이는 히어로 패널. 모바일에서는 숨기고 폼만 보여준다.
// 사진을 패널 전체에 꽉 채우고, 캡션은 사진 위에 얹지 않고 아래 별도 바에 둔다
// (사진 위 그라디언트+텍스트는 흔한 처리라 피한다).
export default function AuthHero({ tagline }: { tagline: string }) {
  return (
    <div className="hidden flex-1 flex-col border-r border-ink/15 lg:flex">
      <div className="flex-1 overflow-hidden">
        <img
          src={golferRabbit}
          alt="AI 캐디 토끼가 홀 공략 정보를 보여주는 모습"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="border-t border-ink/15 bg-paper-2 px-10 py-6">
        <p className="font-display text-2xl leading-snug text-ink">{tagline}</p>
        <p className="mt-2 text-sm text-ink-soft">
          라운드가 쌓일수록 더 정확해지는 AI 골프 코치, GolfMate.
        </p>
      </div>
    </div>
  );
}
