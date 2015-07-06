    public static void Send{name}({param})
    {
        RakNet.BitStream bs = new RakNet.BitStream();

{data}
        Dispatcher.Instance.Send(MsgIDTypes.{msgID}, bs);
    }

