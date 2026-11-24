# ENTER-framed units - the priority list

Functions that begin with `C8` (ENTER). MSC under `/G1` emits `ENTER` for functions with
locals, which is the frame the original uses too - so these units are clear of the frame wall
that blocks most of the `55 8B EC` pool. Round 232 matched the first one worked
(`2a87:0008`, 42 bytes, a `MATCH` with no relocation masking).

**579 units** in the image begin with `C8`. Most of them sit behind another wall, so the list
below is a *superset*: round 232's wall screen (no doubling, no `sub ax,ax` zeroing, no
segment/port/string work, no `B4`-immediate call, no `90` in the body, under 60 bytes) leaves
only **eight**, and those are the ones to work first - they are marked "clear" below.

| va | size | status |
|---|---|---|
| `1ff9:000a` | 24 | open |
| `3a24:0006` | 26 | open |
| `3a5c:0004` | 27 | open |
| `1e9f:0004` | 28 | open |
| `35ec:0098` | 28 | open |
| `3edc:000e` | 28 | open |
| `30fb:008e` | 31 | open |
| `3a58:0024` | 32 | open |
| `1ea4:000a` | 34 | open |
| `1ed7:00de` | 34 | open |
| `2125:000a` | 34 | open |
| `3236:000c` | 34 | open |
| `3aa7:0000` | 34 | open |
| `3eb7:0004` | 34 | open |
| `3316:0006` | 36 | open |
| `3238:0076` | 38 | open |
| `38ad:000e` | 38 | open |
| `396f:000a` | 38 | open |
| `39ff:000a` | 38 | open |
| `3b29:0006` | 38 | open | clear |
| `2e84:000c` | 39 | open |
| `4739:0002` | 39 | open |
| `1f7f:0058` | 40 | open |
| `2421:0002` | 40 | open |
| `2fb5:0008` | 40 | open |
| `3112:000a` | 40 | open |
| `3115:0002` | 40 | open |
| `3831:0004` | 40 | open |
| `3833:000c` | 40 | open |
| `3dd5:0008` | 40 | open |
| `477b:0000` | 40 | MATCHED (round 7) |
| `221a:000a` | 42 | open |
| `330d:001a` | 42 | open |
| `3ddb:000c` | 42 | open |
| `3de2:0002` | 42 | open |
| `3eb4:000a` | 42 | open |
| `4c38:0006` | 42 | open |
| `322c:0000` | 43 | open |
| `2af2:0004` | 44 | open |
| `30fb:014e` | 44 | open |
| `2a6e:000a` | 45 | open |
| `356e:0008` | 45 | open |
| `35ec:0004` | 45 | open |
| `3a30:000c` | 46 | open |
| `3d5a:000c` | 46 | open |
| `3db8:0008` | 46 | MATCHED (round 11) |
| `42fe:000c` | 46 | open |
| `30fb:011e` | 47 | open |
| `374a:000a` | 47 | open |
| `3f44:00bc` | 47 | open |
| `479e:0158` | 47 | open |
| `496b:0004` | 47 | open |
| `4a79:0008` | 47 | open |
| `209c:00cc` | 48 | open |
| `2a8a:0064` | 48 | open |
| `33d7:0000` | 48 | open |
| `34b7:003c` | 48 | open |
| `375a:0008` | 48 | MATCHED (round 12) |
| `3809:0000` | 48 | open | clear |
| `3982:0004` | 48 | open |
| `47c8:000a` | 48 | open | clear |
| `4959:0004` | 48 | open |
| `4a9c:0004` | 48 | open |
| `4f3a:0006` | 48 | open |
| `202b:0006` | 49 | open |
| `3670:0062` | 49 | open |
| `206b:02ec` | 50 | open |
| `3209:0000` | 50 | open |
| `3813:0000` | 50 | open | clear |
| `42cf:0094` | 50 | open |
| `1ec4:007a` | 51 | open |
| `31ca:0002` | 51 | open |
| `33da:0000` | 51 | open |
| `1e1b:0004` | 52 | open |
| `22bb:0004` | 52 | open |
| `2b48:0004` | 52 | open |
| `3353:005a` | 52 | open |
| `3485:0092` | 52 | open |
| `38b9:0000` | 52 | open |
| `1f7f:0000` | 53 | open |
| `3d8a:0006` | 53 | open |
| `23df:0000` | 54 | open |
| `3828:000c` | 54 | open |
| `39b5:0004` | 54 | open |
| `3a15:0008` | 54 | open |
| `4e1f:0004` | 54 | open |
| `1f45:0008` | 55 | open |
| `1f45:0040` | 55 | open |
| `1f45:0078` | 55 | open |
| `2e09:000e` | 55 | open |
| `30fb:00ae` | 55 | open |
| `30fb:00e6` | 55 | open |
| `35f7:0004` | 55 | open |
| `379e:0006` | 55 | MATCHED (round 12) |
| `42b9:0042` | 55 | open |
| `20ae:0008` | 56 | open |
| `2fae:0008` | 56 | open |
| `2fb2:0000` | 56 | open |
| `380d:000c` | 56 | open | clear |
| `3a33:000a` | 56 | open |
| `489c:000a` | 56 | open |
| `48a0:0002` | 56 | open |
| `49ca:00d4` | 56 | open |
| `2fcc:0004` | 57 | open |
| `1ea1:0000` | 58 | open |
| `1f96:0008` | 58 | open |
| `2101:000c` | 58 | open |
| `2a15:0000` | 58 | open |
| `382d:000a` | 58 | open |
| `383b:0004` | 58 | open |
| `383e:000e` | 58 | open |
| `3aaa:0004` | 58 | open |
| `3c05:000c` | 58 | open |
| `4307:000a` | 58 | open |
| `47eb:000e` | 58 | open |
| `4e6a:0000` | 58 | open |
| `1f72:0008` | 59 | open |
| `3376:0076` | 59 | open |
| `496b:0034` | 59 | open |
| `49b2:0054` | 59 | open |
| `21a3:0006` | 60 | open |
| `2387:000c` | 60 | open |
| `2d01:001a` | 60 | open |
| `2eef:004c` | 60 | open |
| `3117:000a` | 60 | open |
| `311b:0006` | 60 | open |
| `322c:0058` | 60 | open |
| `35e8:0008` | 60 | open |
| `366c:0004` | 60 | open |
| `39ef:0004` | 60 | open |
| `39f4:0006` | 60 | open |
| `4fa7:000e` | 60 | open |
| `4516:000c` | 61 | open |
| `2f08:00a4` | 62 | open |
| `313d:0004` | 62 | open |
| `33bd:0008` | 62 | open |
| `3497:0000` | 62 | open |
| `365f:0096` | 62 | open |
| `3746:000c` | 62 | open |
| `4398:0008` | 62 | open |
| `450a:000c` | 62 | open |
| `450e:000a` | 62 | open |
| `4a75:000a` | 62 | open |
| `4c46:005c` | 62 | open |
| `4da6:0004` | 62 | open |
| `2005:0004` | 63 | open |
| `2d40:0006` | 63 | open |
| `33c7:0006` | 63 | open |
| `33c7:0046` | 63 | open |
| `2105:0006` | 64 | open |
| `29ff:0002` | 64 | open |
| `2b7c:00be` | 64 | open |
| `4161:0008` | 64 | open |
| `480b:0008` | 64 | open |
| `480f:0008` | 64 | open |
| `4a5a:00c8` | 64 | open |
| `4c9c:061e` | 64 | open |
| `1e56:000e` | 65 | open |
| `2b25:0006` | 65 | open |
| `2edb:0004` | 65 | open |
| `2eef:000a` | 65 | open |
| `3348:000e` | 65 | open |
| `3368:0000` | 65 | open |
| `36e7:0000` | 65 | open |
| `416f:0000` | 65 | open |
| `4f67:0052` | 65 | open |
| `1e56:0062` | 66 | open |
| `2027:0004` | 66 | open |
| `2edb:0094` | 66 | open |
| `3485:000a` | 66 | open |
| `3616:0064` | 66 | open |
| `37ce:001a` | 66 | open |
| `398d:000c` | 66 | open |
| `3b6a:0000` | 66 | open |
| `4a44:005a` | 66 | open |
| `4dba:0004` | 66 | open |
| `4e29:0000` | 66 | open |
| `1ef8:000c` | 67 | open |
| `3620:0006` | 67 | open |
| `49b2:0090` | 67 | open |
| `231c:0006` | 68 | open |
| `430b:0004` | 68 | open |
| `4512:0008` | 68 | open |
| `2f16:0002` | 69 | open |
| `3485:004c` | 69 | open |
| `5026:005e` | 69 | open |
| `1e1e:008a` | 70 | open |
| `1e2b:0000` | 70 | open |
| `238b:0008` | 70 | open |
| `3879:000a` | 70 | open |
| `2e18:000e` | 71 | open |
| `2f08:000c` | 71 | open |
| `349a:0132` | 71 | open |
| `4ee8:0000` | 71 | open |
| `50b1:002a` | 71 | open |
| `2f3f:0050` | 72 | open |
| `3376:00b2` | 72 | open |
| `35f7:003c` | 72 | open |
| `418c:01e6` | 72 | open |
| `49ad:0008` | 72 | open |
| `4a06:000c` | 72 | open |
| `35c5:0172` | 73 | open |
| `4a0b:0056` | 73 | open |
| `37ff:000c` | 74 | open |
| `4b1f:0002` | 74 | open |
| `2109:0006` | 75 | open |
| `3353:000e` | 75 | open |
| `33e2:0004` | 75 | open |
| `4daf:000c` | 75 | open |
| `4f67:0006` | 75 | open |
| `1df5:0030` | 76 | open |
| `202b:0038` | 76 | open |
| `23e2:0006` | 76 | open |
| `2a2b:0038` | 76 | MATCHED (round 3) | clear |
| `3180:011e` | 76 | open |
| `349a:018a` | 76 | open |
| `3824:0000` | 76 | open |
| `3a5c:0020` | 76 | open |
| `2edb:0046` | 77 | open |
| `3e7f:0136` | 77 | open |
| `4744:00b4` | 77 | open |
| `37f3:0006` | 78 | open |
| `3a68:0008` | 78 | open |
| `4332:0048` | 78 | MATCHED earlier (crelay95.c) | clear |
| `46b0:0006` | 78 | open |
| `2b17:0074` | 79 | open |
| `2f08:0054` | 79 | open |
| `311f:0098` | 79 | open |
| `3972:0000` | 79 | open |
| `3a4a:0002` | 79 | open |
| `3d1c:0000` | 79 | open |
| `43a3:0006` | 79 | open |
| `1ee7:00cc` | 80 | open |
| `33da:0034` | 80 | open |
| `3991:000e` | 80 | open |
| `4c1e:0000` | 80 | open |
| `5021:000e` | 80 | open |
| `2347:000e` | 81 | open |
| `4a0b:0004` | 81 | open |
| `4b6a:0004` | 81 | open |
| `2b3e:0002` | 82 | open |
| `2daf:006e` | 82 | open |
| `3311:0004` | 82 | open |
| `3849:000e` | 82 | open |
| `4291:0008` | 82 | open |
| `495c:0004` | 82 | open |
| `4349:0008` | 83 | open |
| `44f0:0000` | 83 | open |
| `4dd5:0000` | 83 | open |
| `2a7e:0044` | 84 | open |
| `30cf:000a` | 84 | open |
| `4813:0008` | 84 | open |
| `3f0d:0004` | 85 | open |
| `391a:0006` | 86 | open |
| `391f:000c` | 86 | open |
| `5051:000e` | 86 | open |
| `40dc:0000` | 87 | open |
| `4c46:0004` | 87 | open |
| `2a69:0002` | 88 | open |
| `3471:0078` | 88 | open |
| `3eec:0000` | 88 | open |
| `4073:0004` | 88 | open |
| `46db:000c` | 88 | open |
| `46e1:0004` | 88 | open |
| `4da0:000c` | 88 | open |
| `1dfc:000c` | 89 | open |
| `1dfc:008e` | 89 | open |
| `2e25:0000` | 89 | open |
| `3692:02a2` | 89 | open |
| `3bab:0004` | 89 | open |
| `435b:0004` | 89 | open |
| `1e83:0004` | 90 | open |
| `23d1:0006` | 90 | open |
| `3491:0006` | 90 | open |
| `3659:000c` | 90 | open |
| `25d1:0086` | 91 | open |
| `2b34:000e` | 91 | open |
| `4ee1:0014` | 91 | open |
| `364c:0002` | 92 | open |
| `3eec:006a` | 92 | open |
| `4bcd:000a` | 92 | open |
| `4bd3:0006` | 92 | open |
| `4b61:0004` | 93 | open |
| `2f37:000a` | 94 | open |
| `3692:0080` | 94 | open |
| `3730:0006` | 94 | open |
| `3e6a:0008` | 94 | open |
| `4165:0008` | 94 | open |
| `4186:000e` | 94 | open |
| `47c2:000c` | 94 | open |
| `4bc7:000c` | 94 | open |
| `4c2c:0006` | 94 | open |
| `46b5:0004` | 95 | open |
| `2423:000a` | 96 | open |
| `2aec:0004` | 96 | open |
| `34bd:000c` | 96 | open |
| `3646:0002` | 96 | open |
| `4dbf:0000` | 96 | open |
| `2a8a:0002` | 97 | open |
| `2ebb:0004` | 97 | open |
| `3670:0000` | 97 | open |
| `3ede:003e` | 97 | open |
| `23fd:000e` | 98 | open |
| `46d5:000a` | 98 | open |
| `4f61:0004` | 98 | open |
| `3a3f:0002` | 99 | open |
| `3f18:0006` | 99 | open |
| `4e86:0024` | 99 | open |
| `3390:0000` | 100 | open |
| `3653:0008` | 100 | open |
| `3f59:000a` | 100 | open |
| `4aa4:0002` | 100 | open |
| `35ec:0032` | 101 | open |
| `38e5:0000` | 101 | open |
| `3ebd:0002` | 101 | open |
| `2553:000c` | 102 | open |
| `2ad8:000c` | 102 | open |
| `3da5:004e` | 102 | open |
| `3238:000e` | 104 | open |
| `38e5:0066` | 104 | open |
| `242c:000e` | 105 | open |
| `2b17:000a` | 105 | open |
| `324b:00cc` | 105 | open |
| `2a33:0004` | 106 | open |
| `47f1:000a` | 106 | open |
| `4c3f:000a` | 106 | open |
| `2e25:005a` | 107 | open |
| `42e8:0000` | 107 | open |
| `429c:0004` | 108 | open |
| `3a1d:0008` | 109 | open |
| `3348:0050` | 110 | open |
| `4744:0102` | 110 | open |
| `48a0:003a` | 110 | open |
| `4fbb:0004` | 110 | open |
| `211a:000a` | 112 | open |
| `2d59:000e` | 112 | open |
| `2e7b:000e` | 112 | open |
| `3376:0006` | 112 | open |
| `1ec4:0008` | 113 | open |
| `1ef8:00e0` | 114 | open |
| `3390:0266` | 114 | open |
| `2ac2:000e` | 115 | open |
| `2ebb:0190` | 115 | open |
| `3196:000a` | 115 | open |
| `1ff1:0000` | 116 | open |
| `2ee8:0006` | 116 | open |
| `3f34:000e` | 116 | open |
| `2eaa:0006` | 117 | open |
| `2a58:0066` | 118 | open |
| `3670:0094` | 118 | open |
| `2d32:000a` | 119 | open |
| `3692:015c` | 119 | open |
| `1e74:0004` | 120 | open |
| `1e7b:000c` | 120 | open |
| `25c9:000a` | 121 | open |
| `3390:01e0` | 121 | open |
| `2e18:0056` | 122 | open |
| `30dc:000a` | 122 | open |
| `33c7:0086` | 122 | open |
| `347e:0000` | 122 | open |
| `3b62:0006` | 122 | open |
| `2570:0000` | 123 | open |
| `331b:00e4` | 123 | open |
| `4369:0008` | 123 | open |
| `4e11:0002` | 123 | open |
| `30d4:000e` | 124 | open |
| `35c5:01bc` | 124 | open |
| `3912:000a` | 124 | open |
| `3b03:000a` | 124 | open |
| `3b0b:0006` | 124 | open |
| `1ef8:0062` | 125 | open |
| `2f16:0048` | 125 | open |
| `3692:00de` | 125 | open |
| `3692:0000` | 128 | open |
| `25d1:0004` | 129 | open |
| `2f5a:0008` | 129 | open |
| `30fb:000c` | 129 | open |
| `1f0d:0002` | 130 | open |
| `21a7:0002` | 130 | open |
| `2454:0008` | 130 | open |
| `4116:000a` | 130 | open |
| `4c15:000e` | 130 | open |
| `2549:0012` | 131 | open |
| `2ebb:010c` | 131 | open |
| `49e0:000e` | 132 | open |
| `4a79:0038` | 132 | open |
| `4e3c:000c` | 132 | open |
| `206b:0266` | 133 | open |
| `2aae:005e` | 133 | open |
| `328b:0006` | 133 | open |
| `326b:00d6` | 135 | open |
| `3220:001a` | 136 | open |
| `3592:0000` | 136 | open |
| `360e:0006` | 136 | open |
| `2b7c:0034` | 137 | open |
| `2b69:0000` | 138 | open |
| `307b:040e` | 138 | open |
| `31c1:0008` | 138 | open |
| `3979:000a` | 138 | open |
| `435b:005e` | 138 | open |
| `5057:0004` | 138 | open |
| `2560:000e` | 139 | open |
| `25f0:0006` | 139 | open |
| `3600:005a` | 140 | open |
| `42cf:0006` | 141 | open |
| `1f66:000e` | 142 | open |
| `39be:0002` | 142 | open |
| `365f:0006` | 143 | open |
| `42b0:000c` | 144 | open |
| `2f22:0014` | 145 | open |
| `39e0:0002` | 145 | open |
| `344e:000c` | 147 | open |
| `4e76:000c` | 147 | open |
| `311f:00e8` | 149 | open |
| `5026:00a4` | 150 | open |
| `355c:0000` | 151 | open |
| `234d:0000` | 152 | open |
| `2eaa:007c` | 152 | open |
| `2141:0008` | 153 | open |
| `4f22:000e` | 155 | open |
| `1e4b:000e` | 156 | open |
| `3d99:002e` | 156 | open |
| `3f03:0008` | 156 | open |
| `35ab:0002` | 157 | open |
| `2d1f:0002` | 158 | open |
| `316e:0002` | 158 | open |
| `3692:02fc` | 158 | open |
| `3e70:0006` | 158 | open |
| `2efe:000c` | 160 | open |
| `2a93:0004` | 161 | open |
| `2af5:0000` | 162 | open |
| `1fb5:0004` | 164 | open |
| `3368:0042` | 164 | open |
| `2dce:0158` | 165 | open |
| `2ebb:0066` | 165 | open |
| `2f77:0000` | 166 | open |
| `3a7c:000c` | 166 | open |
| `2220:0000` | 168 | open |
| `4529:0000` | 169 | open |
| `4744:000a` | 169 | open |
| `4c9c:0848` | 169 | open |
| `3620:01b8` | 170 | open |
| `32c5:000e` | 171 | open |
| `37b3:0024` | 171 | open |
| `4c9c:079c` | 171 | open |
| `4a0b:00a0` | 172 | open |
| `2b71:000a` | 176 | open |
| `3141:00f8` | 176 | open |
| `3620:004a` | 177 | open |
| `3a6f:000e` | 179 | open |
| `38bc:0004` | 180 | open |
| `4f9c:0006` | 184 | open |
| `2410:0000` | 186 | open |
| `3620:00fc` | 187 | open |
| `4a5a:000c` | 187 | open |
| `33e2:0050` | 188 | open |
| `209c:000e` | 190 | open |
| `50a5:000a` | 190 | open |
| `1fe2:0020` | 191 | open |
| `2320:000a` | 192 | open |
| `3acb:000a` | 192 | open |
| `4533:000a` | 192 | open |
| `36cb:000a` | 193 | open |
| `335b:000e` | 194 | open |
| `30eb:0048` | 196 | open |
| `3c09:0288` | 196 | open |
| `341d:016a` | 197 | open |
| `4a84:000c` | 198 | open |
| `23f1:0006` | 199 | open |
| `49ca:000c` | 199 | open |
| `38f1:000e` | 200 | open |
| `4dfa:0008` | 201 | open |
| `42db:0006` | 202 | open |
| `3692:01d4` | 206 | open |
| `45b3:0002` | 206 | open |
| `4b23:002c` | 206 | open |
| `4b50:000e` | 206 | open |
| `4e9d:0000` | 206 | open |
| `3196:007e` | 207 | open |
| `326b:0006` | 207 | open |
| `324b:0136` | 208 | open |
| `46c8:000a` | 208 | open |
| `4a4d:000c` | 208 | open |
| `454c:000e` | 210 | open |
| `4abc:0056` | 210 | open |
| `1e60:0004` | 212 | open |
| `4c08:000a` | 212 | open |
| `357f:0002` | 213 | open |
| `46b5:0064` | 214 | open |
| `2134:0000` | 216 | open |
| `328b:008c` | 218 | open |
| `331b:0008` | 219 | open |
| `257f:000c` | 220 | open |
| `356e:0036` | 220 | open |
| `4f22:00aa` | 220 | open |
| `32a1:0006` | 222 | open |
| `32af:0004` | 222 | open |
| `4093:00f6` | 223 | open |
| `466b:0000` | 224 | open |
| `5040:003e` | 224 | open |
| `384f:0000` | 226 | open |
| `4f14:000a` | 228 | open |
| `4fdb:0000` | 228 | open |
| `245c:000a` | 230 | open |
| `48c7:000a` | 230 | open |
| `4e58:0038` | 232 | open |
| `4727:0002` | 233 | open |
| `43b0:00a6` | 235 | open |
| `341d:0230` | 236 | open |
| `5004:0004` | 236 | open |
| `2362:013e` | 238 | open |
| `477b:0146` | 238 | open |
| `5013:0000` | 238 | open |
| `477b:0054` | 241 | open |
| `36cb:00cc` | 243 | open |
| `24cb:000c` | 245 | open |
| `50c7:00b2` | 250 | open |
| `3cc2:0002` | 252 | open |
| `20e4:000a` | 260 | open |
| `37da:0004` | 260 | open |
| `4d88:0004` | 261 | open |
| `3bdc:000e` | 262 | open |
| `35ab:00a0` | 264 | open |
| `20b4:0026` | 265 | open |
| `48d6:0000` | 265 | open |
| `3e7f:0006` | 273 | open |
| `2f65:000e` | 274 | open |
| `3680:000a` | 278 | open |
| `3180:0006` | 279 | open |
| `4c9c:0684` | 279 | open |
| `4693:00b8` | 286 | open |
| `3c09:001c` | 289 | open |
| `349a:000e` | 291 | open |
| `3aad:000e` | 294 | open |
| `4760:0006` | 299 | open |
| `34dd:0008` | 308 | open |
| `2362:0008` | 309 | open |
| `3a02:0000` | 312 | open |
| `375e:0040` | 313 | open |
| `479e:001c` | 315 | open |
| `3d1c:0050` | 325 | open |
| `5080:000c` | 327 | open |
| `3c09:013e` | 329 | open |
| `405e:0002` | 338 | open |
| `418c:0084` | 344 | open |
| `44f0:0054` | 344 | open |
| `3f18:006a` | 356 | open |
| `341d:0002` | 359 | open |
| `35c5:0008` | 361 | open |
| `3196:014e` | 362 | open |
| `3783:000e` | 371 | open |
| `459b:0008` | 378 | open |
| `3390:0064` | 379 | open |
| `331b:0160` | 382 | open |
| `3c8f:0008` | 392 | open |
| `3ca8:0000` | 418 | open |
| `3927:000e` | 420 | open |
| `399a:000c` | 424 | open |
| `2f92:0000` | 456 | open |
| `246f:0002` | 470 | open |
| `4d6a:000e` | 470 | open |
| `307b:021e` | 495 | open |
| `4be5:000a` | 560 | open |
| `418c:0274` | 599 | open |
| `206b:0000` | 614 | open |
| `24a4:0002` | 634 | open |
| `4af7:0004` | 638 | open |
| `33f2:000c` | 678 | open |
| `3cd1:000e` | 739 | open |
| `258d:0008` | 785 | open |
| `4c61:0004` | 805 | open |
| `44a4:0124` | 814 | open |
| `455a:0000` | 833 | open |
| `238f:000e` | 918 | open |
| `4b7d:000a` | 1186 | open |
| `4c9c:008e` | 1423 | open |
| `45b3:00d0` | 1747 | open |
| `3fcf:0036` | 1786 | open |
| `41ef:0004` | 2087 | open |

Groups worth noticing in the open ones: three consecutive units (`3809:0000`,
`380d:000c`, `3813:0000`) look like nibble/bit-swap routines over the same two locals -
likely one small family; `2a2b:0038` and `4332:0048` are long-arithmetic loops.

## What the remaining clear units are (round 235)

Decoded far enough to say what they do, even where they are not yet transcribed:

- **`3809:0000`, `380d:000c`, `3813:0000`** - a family of **nibble transforms** on a two-byte
  value. Each takes the parameter into a two-byte local, then mixes the two bytes' nibbles with
  `and 0x0F` / `shr 4` / `shl 4` / `xor` and stores the result back. `3813:0000` is the clearest
  (`and dx,0x0F`; `shr cx,4`; `xor cl,al`; `shl dx,4`; `xor al,dl`; `and ax,0xF000`), which
  reads like a small scrambling or checksum routine over a 16-bit value. Three members means a
  transcription that works would pay three rows.
- **`2a2b:0038`** (76 B) and **`4332:0048`** (78 B) are long-arithmetic loops: the first does
  two subtractions of a `long` delta and a signed comparison against a threshold before
  storing, the second walks a table at `0x866E` in four-byte steps.
- **`3b29:0006`** (38 B) is an exchange (`old = g; g = v; return old;`) - blocked by the BX
  save, wall 20.

None is recorded as a row. The nibble family is the one worth another attempt: it is the only
group where three rows sit behind a single source shape.

### The nibble family: what is settled and what is not (round 236)

Four source shapes were compiled for `3813:0000`. What the attempts establish:

- the function has **one two-byte local** (`C8 02 00 00`) - `x`, held at `[bp-2]`;
- it uses **DX/DL as scratch**, not the frame;
- the operations are two `xor`s into `x`: one built from `((a >> 4) ^ a) & 0x0F` and one from
  `(a & 0x0F) << 4`, with the second operand pair computed **before** the first `xor` - so the
  source reads `x = a;` then two `^=` statements whose right-hand sides both use `a`.

MSC gets the frame right when the source uses a single local, but then it loads the parameter
into **CX** where the original loads **AX** (register naming again), and with two locals the
frame doubles to four bytes and the shape diverges at the first instruction.

Not recorded. The translation is close - two instructions of the whole function are wrong - but
"close" is not this ledger's standard, and the family is worth another attempt with the
scratch-register requirement in mind.

### Two more shapes, and the exact blocker (round 237)

Rounding out round 236: with the second `xor` written to use the `0xF000` mask the original
applies (`x ^= (x ^ ((a & 0x0F) << 4)) & 0xF000;`), the object still differs at offset 4 - MSC
loads the parameter as a **byte** (`8A 46 04`) where the original loads the **word**
(`8B 46 04`), because by that point only the low byte has been used.

That is the narrowing wall (19) again, in a new place: it is not a mask on a parameter this
time, it is MSC proving the high byte unused *because the source as written does not use it*.
The original's later `and ax,0xF000` is a use - which suggests its source really does keep the
high byte live throughout, rather than via a temporary.

So the chain of blockers for this one function is now: one two-byte local (settled), DX as
scratch (settled), CX instead of AX for the shift (wall 6), byte-narrowing of the parameter
(wall 19). Four source shapes in two rounds have each moved the difference by one instruction
and none has closed it.

The family stays open and documented. It is a good example of a candidate that is *understood*
and not *reproducible*, which is the category the project has spent its last forty rounds
mapping.

### Round 1 of the new session: nine more shapes, no change

Nine further spellings of `3813:0000` (plain, `volatile` local, union, byte pointer, scoped temporary; `/Od /Ox /Os`) never gave the original's `mov [bp-2],ax` then `mov dl,[bp-2]` start. MSC either drops the local (`55 8B EC`, no `C8`) or loads the parameter byte-wise. Same two walls (6, 19); family stays open.

### Round 2: 47c8:000a (48 B, far, clears 11 words after +0x2c and counts the non-zero ones)

Twelve spellings (array/pointer, `register`, do-while, spare local; `/Ox`, `/Os`). `/Ox` gives the right loop and `C8 02` with a spare local, but keeps the count in DI and the counter in CX; the original counts in CX and loops on DI, and emits `xor cx,cx` before the argument loads. `/Os` spills everything to the frame. Same register-naming wall (CX is MSC's scratch); not recorded.

### Round 5: four of the shortest open units, all walled

- `1ff9:000a` (24 B): `les ax,[bp+6]` + `mov ax,es` into a local - MSC folds the high word to `mov ax,[bp+8]` under every flag set (nine spellings: cast, `FP_SEG`, union, `volatile`). Not reachable.
- `3edc:000e` (28 B): `(*g(n)) >> 6` with a far callee. Right code except `mov bx,ax` / `mov es,dx` come in the opposite order (HOWTO 4.8).
- `3a24:0006` (26 B): `g(n)->v = 0` - the original keeps the offset in SI (HOWTO 4.9); MSC uses BX.
- `3a5c:0004`, `1e9f:0004`, `35ec:0098`: contain `90 0E E8` / far-call relays; not tried this round.
- Note: the *open* column of this table is stale for at least `4332:0048` (already a ledger row, crelay95.c); check MATCHING.md before starting a unit.

### Round 6: screened list, and 4349:005c

A byte screen (ENTER-framed, not already a ledger row, <= 80 B, no `90`, no far-call relay, no doubling, no `sub ax,ax`, no `B4`) leaves 64 units; the short ones are mostly `call 7cb8` + `mov si,ax` / `es:` field accessors (SI-holder wall, HOWTO 4.9) or `les` word extraction (see round 5).

`4349:005c` (33 B, far): counts entries of the 64 four-byte records at 0x866E whose first word has `(w & 0x7ff) != 0x7ff`. The body matches byte for byte under `/Ox` (`xor dx,dx` / `mov bx,866e` / `and ah,7` / `cmp ax,7ff` ... `jb`), but the original has `C8 02` with a **never-used** local. MSC drops an unused local; making it used (`volatile`, address taken, read-back) inserts stores and moves BX. Nine spellings, no match; the remaining difference is only the frame (`C8 02 00 00` / `C9` vs none).

No ledger change, so verify.py was not re-run this round.

### Round 8: long exchange, 1e33:0006 and 2d46:0008

`long old = g; g = v; return old;` (far pascal, `C8 04`). Eight spellings (plain, extra local, `register`, union, split lo/hi) give the right frame under `/Ox` but the old low word goes to `[bp-4]` where the original keeps it in **BX** (`mov bx,ax` ... `mov ax,bx`). That is the BX wall (BX is never a C variable). `2d46:0008` is the same function on an `es:`-addressed global (segment 4827) and shares the wall. Not recorded. `477b:0000` (round 7) was the only ENTER unit that closed this way.

### Round 9: 42fe:000c, 4978:000a

- `42fe:000c` (44 B, far): sums byte field `[bx+2]` over the records at 0x866E whose sign-extended 11-bit key (`shl ax,5; sar ax,5`) equals the argument. Bit-field spelling gives the body byte for byte under `/Ox`; only the frame differs (original `C8 02` with an unused local, MSC emits `55 8B EC`). Same frame-only miss as `4349:005c` (round 6); eight spellings of a dead local (assigned, initialised, array, address taken) are all dropped.
- `4978:000a` (44 B): `r = i = 0` stored through the frame (`xor ax,ax; mov [bp-2],ax; mov [bp-4],ax`) around a loop of 35 near calls `r |= G(i,p)`. MSC register-allocates r and i under `/Ox` (`xor dx,dx` ...) and uses `mov [bp-x],0` under `/Os`; neither gives the shared-zero store. Six spellings, no match.

Open question worth one test: do any two frame-only misses (`4349:005c`, `42fe:000c`) share a *used-but-optimised-away* local that a different construct keeps alive?

### Round 10: third frame-only miss, and a test of the dead-local idea

- `4a03:000c` (48 B, far): counts leading entries of 32 far pointers at 0x9973 that are non-null and (when the argument is 0) point at a word >= 0x20. Four spellings give the body under `/Ox` with only the frame different (`C8 02` vs `55 8B EC`). Third unit of this kind with `4349:005c` and `42fe:000c`.
- Test of round 9's question: on `4349:005c` a local that is *used* (`long t; t=1; t<<=1;`, a struct local, a char array) is simply optimised away; the object has **no frame at all** (no `55 8B EC`, `retf` direct). So under `/Ox` no source-level local survives when the function body does not need one; the original's `C8 02` frame is not explainable by a live variable. Three units / ~125 B behind it; no source route.

### Round 13: 39b5:0004 and 2033:0004

- `39b5:0004` (54 B): `p = G(n); *px = p->x + 1; *py = p->y + 1; H(n,0,0);` The original keeps `n` in DI and the returned pointer in BX/ES (`mov bx,ax; mov es,dx`), and the first two loads go through `es:` twice. Eight spellings (plain, `register` on `p` or `n`, spare local) all fail at byte 0 or 4 (`55 8B EC` vs `C8`, `56 57` vs `57 56`): BX wall plus the push-order tell. Not recorded.
- `2033:0004` is listed as 54 B but is a **cut window**: the function runs on past `0x35` (`mov [bp-0xc],ax` is followed by five `lea`/`push ss` pairs, a `call far 25ca:174a` and a second half past `0x70`), so the true size is well over 100 B. Do not take 54 from this table.

### Round 14: 38d2:0006, 382d:000a (both near misses, both register allocation)

- `38d2:0006` (54 B): `p = G(n); i = 0; while (p->cnt > i) i = H(n,i);` Body matches; the original executes `mov di,[bp+6]` *before* `xor si,si` and keeps the pointer only in `[bp-4]`, MSC hoists `xor si,si` first and also copies the offset into DI (`mov di,bx`). Four loop spellings, same result.
- `382d:000a` (58 B): `p = G(n); r = K(p->f); p->f = *L(v,&t); return r;` The original saves only SI (`r`) and leaves `p` in the frame; MSC saves DI and SI (`r` in DI, a second copy of the pointer offset in SI). Prologue differs at byte 4 (`56` vs `57 56`). Six spellings including `register`.
- Next untried from the screen: `39f9:0006` (bit-field insert, `sub al,al` wall suspected), `2162:0006` (switch), `4b5d:000c`, `4307:000a` (`ret 6`, byte fields in a 4-byte record).

### Round 15: 4307:000a, and a read of the PENDING list

- `4307:000a` (58 B, near, `ret 6`): clamp-add on byte field `[rec+2]` of a 4-byte record (`if (len + n > max) n = max - len; len += n; return n`). With a plain `unsigned char` field MSC gives the same compare/subtract body but `55 8B EC` and a byte `add [bx+2],dl`; with an `unsigned len:8` bit-field it does the word read-modify-write the original has, but via BX and a `push si` only at the end. The original keeps the record pointer in SI and has `C8 02`. Seven spellings. BX wall again.
- All 38 PENDING notes re-read: the residues are pad bytes (`90`), `add r,r` doubling, shared `ret`, `xor` vs `mov ax,0`, BX/SI roles, `les` splits - each already on the proven-unreachable list. No PENDING row has an untested source-level lever.
