select @RNUM := @RNUM + 1 AS NO, 'test' aaa, 'test2' bbb, 'test3' ccc, a.name, b.email, 
       case when a.status = 'downloadable' then '생성완료'
            when a.status = 'notpassing' then '생성 전'
            when a.status = 'generated' then '생성오류' else '' end status
  from ( SELECT @RNUM := 0 ) b, certificates_generatedcertificate a inner join auth_user b
    on (a.user_id = b.id)
 where b.email like '%hero%';
 

      


select course_id,email 
from certificates_generatedcertificate a inner join auth_user b
  on a.user_id = b.id
where b.email  like '%hero%';

