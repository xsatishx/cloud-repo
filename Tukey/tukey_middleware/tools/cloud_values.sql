--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: cloud; Type: TABLE DATA; Schema: public; Owner: cloudgui
--

COPY cloud (cloud_id, cloud_name, auth_url, login_url, display_name) FROM stdin;
6	aws	\N	\N	\N
3	sullivan	http://10.103.114.3:5000/v2.0/	http://10.103.114.1:5005	Sullivan
2	adler	\N	http://10.103.112.1:5005	Adler
8	cobb	\N	\N	Cobb
7	goldberg	\N	\N	Goldberg
5	atwood	http://10.103.105.2:5000/v2.0/	http://10.103.105.1:5005	Atwood
\.


--
-- PostgreSQL database dump complete
--
