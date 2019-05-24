#!/usr/bin/fish

function try_signin_once --description "signin_once <openid> <N> <E> <tmpfl> <cookiefl>"
    set _openid $argv[1]
    set _NorthLatitude $argv[2]
    set _EastLongitude $argv[3]
    set cookiefl $argv[4]

    set tmpfl (mktemp)
    set result_success 0
    set result_failed 1
    set result_badid 2
    set result_nothing 3

    set _url "https://v18.teachermate.cn/wechat/wechat/guide/signin?openid=$_openid"
    set _resign_url "https://v18.teachermate.cn/api/v1/wechat/re-auth?m=s_signin&code=$_openid&state=$_openid"
    curl -L "$_url" -v 2>$cookiefl > $tmpfl
    curl -L "$_resign_url" -v 2>$cookiefl > $tmpfl
    if grep -F '{"data":\[\],"msg":"unauthorized"}' $tmpfl > /dev/null
        return $result_badid
    end
    if grep -F '401 Unauthorized' $cookiefl > /dev/null
        return $result_badid
    end
    if grep -F '签到中...' $tmpfl > /dev/null
        ################## Real signin!!!
        # set _courseid (curl "$_url" -v 2>&1 | grep '^< Location: ' | sed 's/^.*course_id=//')
        set _courseid (cat "$tmpfl" | grep 'id="course-id' | sed 's/^.*value="//g' | sed 's/" .*$//g')
        set _signid (cat "$tmpfl" | grep 'id="sign-id' | sed 's/^.*value="//g' | sed 's/" .*$//g')
        # set _wx_csrf (grep 'Set-Cookie' $cookiefl | sed 's/^.*wx_csrf_cookie=//' | sed 's/;.*$//')
        set _wx_csrf (cat "$tmpfl" | grep 'id="token-hash' | sed 's/^.*value="//g' | sed 's/" .*$//g')
        # recolic: they changed `www.teachermate.com.cn` to `v18.teachermate.com.cn` but doesn't provide new certificate... I added -k here. (which indicates that their client (wechat and dingtalk) doesn't check certificate at all)
        curl -k "https://v18.teachermate.com.cn/wechat-api/v1/class-attendance/student-sign-in" --data "openid=$_openid&courseId=$_courseid&lon=$_EastLongitude&lat=$_NorthLatitude&signId=$_signid&wx_csrf_name=$_wx_csrf" > $cookiefl 2>/dev/null
        grep -F 'repeat sign in' $cookiefl > /dev/null; and return $result_nothing
        # print the signRank if success
        grep -F 'signRank' $cookiefl; and return $result_success; or return $result_failed
        ################## Real signin end!!!
    end
    if grep -F "<p class='success-tip'>暂无开启的签到" $tmpfl > /dev/null
        return $result_nothing
    end
    if grep -F '你已签过到了' $tmpfl > /dev/null
        return $result_nothing
    end
end

if test (count $argv) != '4'
    echo 'Usage: signin_once <openid> <N> <E> <cookiefl>'
    exit 6
end
try_signin_once $argv[1..-1]
exit $status
