PGDMP      8                |           test    16.0    16.0 (    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    17021    test    DATABASE     x   CREATE DATABASE test WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_Israel.1252';
    DROP DATABASE test;
                postgres    false                        3079    17022 	   adminpack 	   EXTENSION     A   CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;
    DROP EXTENSION adminpack;
                   false            �           0    0    EXTENSION adminpack    COMMENT     M   COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';
                        false    2            �            1259    17032    grades    TABLE     �   CREATE TABLE public.grades (
    id integer NOT NULL,
    name text NOT NULL,
    hours_per_subject json NOT NULL,
    max_hours_per_day integer NOT NULL,
    max_hours_per_friday integer NOT NULL
);
    DROP TABLE public.grades;
       public         heap    postgres    false            �            1259    17037    Grades_ID_seq    SEQUENCE     �   ALTER TABLE public.grades ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Grades_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    216            �            1259    17038 
   classrooms    TABLE     q   CREATE TABLE public.classrooms (
    id integer NOT NULL,
    name text NOT NULL,
    available json NOT NULL
);
    DROP TABLE public.classrooms;
       public         heap    postgres    false            �            1259    17043    classrooms_classroom_id_seq    SEQUENCE     �   ALTER TABLE public.classrooms ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.classrooms_classroom_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    218            �            1259    17044    default_teachers    TABLE     �   CREATE TABLE public.default_teachers (
    id integer NOT NULL,
    name text NOT NULL,
    is_teacher boolean NOT NULL,
    password text NOT NULL,
    subject_id integer,
    work_hours_json json
);
 $   DROP TABLE public.default_teachers;
       public         heap    postgres    false            �            1259    17049    default_teachers_id_seq    SEQUENCE     �   ALTER TABLE public.default_teachers ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.default_teachers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    220            �            1259    17050    lessons    TABLE     �   CREATE TABLE public.lessons (
    hour bigint,
    day bigint,
    classroom_id bigint,
    teacher_id bigint,
    grade_id bigint
);
    DROP TABLE public.lessons;
       public         heap    postgres    false            �            1259    17053    subjects    TABLE     z   CREATE TABLE public.subjects (
    id integer NOT NULL,
    name text NOT NULL,
    max_hours_per_day integer NOT NULL
);
    DROP TABLE public.subjects;
       public         heap    postgres    false            �            1259    17058    subjects_subject_id_seq    SEQUENCE     �   ALTER TABLE public.subjects ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.subjects_subject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    223            �            1259    17059    users    TABLE     �   CREATE TABLE public.users (
    id integer NOT NULL,
    name text NOT NULL,
    is_teacher boolean NOT NULL,
    password text NOT NULL,
    work_hours_json json,
    subject_id integer
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    17064    users_user_id_seq    SEQUENCE     �   ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    225            �          0    17038 
   classrooms 
   TABLE DATA           9   COPY public.classrooms (id, name, available) FROM stdin;
    public          postgres    false    218   �+       �          0    17044    default_teachers 
   TABLE DATA           g   COPY public.default_teachers (id, name, is_teacher, password, subject_id, work_hours_json) FROM stdin;
    public          postgres    false    220   �+       �          0    17032    grades 
   TABLE DATA           f   COPY public.grades (id, name, hours_per_subject, max_hours_per_day, max_hours_per_friday) FROM stdin;
    public          postgres    false    216   �+       �          0    17050    lessons 
   TABLE DATA           P   COPY public.lessons (hour, day, classroom_id, teacher_id, grade_id) FROM stdin;
    public          postgres    false    222   ,       �          0    17053    subjects 
   TABLE DATA           ?   COPY public.subjects (id, name, max_hours_per_day) FROM stdin;
    public          postgres    false    223   !,       �          0    17059    users 
   TABLE DATA           \   COPY public.users (id, name, is_teacher, password, work_hours_json, subject_id) FROM stdin;
    public          postgres    false    225   >,       �           0    0    Grades_ID_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public."Grades_ID_seq"', 1, false);
          public          postgres    false    217            �           0    0    classrooms_classroom_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.classrooms_classroom_id_seq', 1, false);
          public          postgres    false    219            �           0    0    default_teachers_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.default_teachers_id_seq', 1, false);
          public          postgres    false    221            �           0    0    subjects_subject_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.subjects_subject_id_seq', 1, false);
          public          postgres    false    224            �           0    0    users_user_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);
          public          postgres    false    226            4           2606    17066    grades Grades_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.grades
    ADD CONSTRAINT "Grades_pkey" PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.grades DROP CONSTRAINT "Grades_pkey";
       public            postgres    false    216            8           2606    17068    classrooms classrooms_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.classrooms DROP CONSTRAINT classrooms_pkey;
       public            postgres    false    218            <           2606    17070 &   default_teachers default_teachers_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.default_teachers
    ADD CONSTRAINT default_teachers_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.default_teachers DROP CONSTRAINT default_teachers_pkey;
       public            postgres    false    220            >           2606    17072    subjects subjects_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.subjects DROP CONSTRAINT subjects_pkey;
       public            postgres    false    223            :           2606    17074    classrooms unique_classroomname 
   CONSTRAINT     Z   ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT unique_classroomname UNIQUE (name);
 I   ALTER TABLE ONLY public.classrooms DROP CONSTRAINT unique_classroomname;
       public            postgres    false    218            6           2606    17076    grades unique_gradename 
   CONSTRAINT     R   ALTER TABLE ONLY public.grades
    ADD CONSTRAINT unique_gradename UNIQUE (name);
 A   ALTER TABLE ONLY public.grades DROP CONSTRAINT unique_gradename;
       public            postgres    false    216            @           2606    17078    subjects unique_name 
   CONSTRAINT     O   ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT unique_name UNIQUE (name);
 >   ALTER TABLE ONLY public.subjects DROP CONSTRAINT unique_name;
       public            postgres    false    223            C           2606    17080    users unique_username 
   CONSTRAINT     P   ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_username UNIQUE (name);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT unique_username;
       public            postgres    false    225            E           2606    17082    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    225            A           1259    17083    fki_fk_subject    INDEX     F   CREATE INDEX fki_fk_subject ON public.users USING btree (subject_id);
 "   DROP INDEX public.fki_fk_subject;
       public            postgres    false    225            G           2606    17084    users fk_subject    FK CONSTRAINT     u   ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_subject FOREIGN KEY (subject_id) REFERENCES public.subjects(id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT fk_subject;
       public          postgres    false    223    4670    225            F           2606    17089    default_teachers fk_subject    FK CONSTRAINT     �   ALTER TABLE ONLY public.default_teachers
    ADD CONSTRAINT fk_subject FOREIGN KEY (subject_id) REFERENCES public.subjects(id);
 E   ALTER TABLE ONLY public.default_teachers DROP CONSTRAINT fk_subject;
       public          postgres    false    223    220    4670            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   ;   x�3�LL����L�42426J3�4O4�DscK�D�T�Dôdc�? ����� z��     