-- INSERT INTO public.times (doctor_name,weekday,shift,hour,date,capacity,visit_count)
-- VALUES ('مسعوده سبزه چیان','سه شنبه','عصر','16:00','2/25/1403',25,0)

-- INSERT INTO public.clinics (section,clinic)
-- VALUES ('فوق تخصص خون اطفال','کلینیک کودکان و اطفال')

-- INSERT INTO public.doctors (name,code,section,expertise,shifts)
-- VALUES ('مسعوده سبزه چیان',68834,'فوق تخصص کلیه اطفال','فوق تخصص کلیه اطفال','صبح،عصر')

SELECT * FROM public.times

-- DELETE FROM public.clinics WHERE section = 'فوق تخصص خون اطفال'

-- UPDATE public.times
-- SET capacity = 20,visit_count = 0
-- WHERE id=6