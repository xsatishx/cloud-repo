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
-- Data for Name: login_method; Type: TABLE DATA; Schema: public; Owner: cloudgui
--

COPY login_method (method_id, method_name) FROM stdin;
2	openid
3	shibboleth
\.


--
-- PostgreSQL database dump complete
--
