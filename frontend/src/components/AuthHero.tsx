import golferRabbit from '../assets/golfer-rabbit.png';

// 로그인/회원가입 페이지 좌측에 쓰이는 히어로 패널. 모바일에서는 숨기고 폼만 보여준다.
export default function AuthHero({ tagline }: { tagline: string }) {
  return (
    <div className="relative hidden overflow-hidden lg:flex lg:w-1/2">
      <img
        src={golferRabbit}
        alt="AI 캐디 토끼가 홀 공략 정보를 보여주는 모습"
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-emerald-950 via-emerald-950/30 to-emerald-950/10" />
      <div className="relative mt-auto p-10">
        <p className="text-sm uppercase tracking-widest text-emerald-300">GolfMate AI</p>
        <p className="mt-2 max-w-sm text-xl font-medium text-emerald-50">{tagline}</p>
      </div>
    </div>
  );
}
